#!/usr/bin/env python3
"""Robustness checks for an availability-only cloud-service reconstruction.

The input table contains public service-availability records from the Google Cloud
europe-west2 incident of 19-20 July 2022. Six records with numerical availability
fractions form the baseline calculation. The module performs baseline reproduction,
threshold sensitivity, leave-one-cohort-out analysis, two Filestore time readings,
and cohort-contribution analysis.

The aggregate is a normalized service-availability index. It is not a measurement of
workload-level compute delivery. All arithmetic uses ``fractions.Fraction`` and all
outputs are written with the Python standard library.
"""

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_CSV = os.path.join(ROOT, "data", "service_cohorts.csv")
RESULTS_DIR = os.path.join(ROOT, "results")

TIME_FMT = "%Y-%m-%d %H:%M"
WINDOW_MINUTES = 1155
ILLUSTRATIVE_THRESHOLD = Fraction(8, 10)


@dataclass(frozen=True)
class Metrics:
    """Exact aggregate metrics for one analysis case.

    ``final_recovery_minutes`` is ``None`` when recovery is not observed before
    the fixed observation window ends. A value of zero means the index never fell
    below the selected threshold.
    """

    minimum_availability_index: Fraction
    time_below_threshold_minutes: int
    final_recovery_minutes: Optional[int]
    wsdh_hours: Fraction

    @property
    def recovery_observed(self):
        return self.final_recovery_minutes is not None

    @property
    def right_censored(self):
        return self.final_recovery_minutes is None


def _parse_dt(value):
    return datetime.strptime(value.strip(), TIME_FMT)


def load_cohorts(path=DATA_CSV):
    """Read the machine-readable cohort table as a list of dictionaries."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def available_fraction(row):
    """Return an exact available fraction, or ``None`` when none was reported.

    Exact population counts take precedence over rounded fractions. Missing values
    are not imputed.
    """
    population = row["reported_population"].strip()
    impacted = row["reported_impacted_count"].strip()
    if population.isdigit() and impacted.isdigit():
        return Fraction(int(population) - int(impacted), int(population))
    value = row["reported_available_fraction"].strip()
    if value in ("", "n/a"):
        return None
    return Fraction(value)


def included_rows(rows):
    return [row for row in rows if row["inclusion_status"].strip() == "included"]


def _offset(moment, origin):
    return int((moment - origin).total_seconds() // 60)


def window_origin(rows):
    """Return the earliest UTC impact start among the supplied rows."""
    return min(_parse_dt(row["impact_start_utc"]) for row in rows)


def build_windows(rows, origin):
    """Return ``(id, available_fraction, start_minute, end_minute)`` tuples.

    Rows without a numerical available fraction are skipped rather than imputed.
    """
    windows = []
    for row in rows:
        fraction = available_fraction(row)
        if fraction is None:
            continue
        start = _offset(_parse_dt(row["impact_start_utc"]), origin)
        end = _offset(_parse_dt(row["impact_end_utc"]), origin)
        windows.append((row["cohort_id"].strip(), fraction, start, end))
    return windows


def availability_series(windows, window_minutes=WINDOW_MINUTES):
    """Calculate the equal-weight aggregate availability index minute by minute."""
    if not windows:
        raise ValueError("at least one cohort window is required")
    if window_minutes <= 0:
        raise ValueError("window_minutes must be positive")
    weight = Fraction(1, len(windows))
    series = []
    for minute in range(window_minutes):
        fractions = [
            available if start <= minute < end else Fraction(1)
            for _, available, start, end in windows
        ]
        series.append(sum(fractions) * weight)
    return series


def compute_metrics(windows, threshold, window_minutes=WINDOW_MINUTES):
    """Compute aggregate availability metrics for one case.

    Recovery is the first minute after the final below-threshold observation. If the
    final observation is still below threshold, recovery is unobserved and represented
    by ``None`` rather than by the observation-window length.
    """
    series = availability_series(windows, window_minutes)
    below_minutes = [minute for minute, value in enumerate(series) if value < threshold]
    if not below_minutes:
        recovery = 0
    elif below_minutes[-1] == window_minutes - 1:
        recovery = None
    else:
        recovery = below_minutes[-1] + 1
    return Metrics(
        minimum_availability_index=min(series),
        time_below_threshold_minutes=len(below_minutes),
        final_recovery_minutes=recovery,
        wsdh_hours=sum(Fraction(1) - value for value in series) / Fraction(60),
    )


def fmt10(value):
    """Format a numerical value to ten decimal places."""
    return format(float(value), ".10f")


def baseline(rows):
    selected = included_rows(rows)
    origin = window_origin(selected)
    windows = build_windows(selected, origin)
    return windows, compute_metrics(windows, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES)


def cohort_contributions(rows):
    """Return per-cohort duration, available fraction, and deficit hours."""
    selected = included_rows(rows)
    origin = window_origin(selected)
    windows = build_windows(selected, origin)
    total_unweighted = Fraction(0)
    contributions = []
    for cohort_id, available, start, end in windows:
        duration = end - start
        deficit = (Fraction(1) - available) * Fraction(duration, 60)
        total_unweighted += deficit
        contributions.append({
            "cohort_id": cohort_id,
            "duration_minutes": duration,
            "available_fraction": available,
            "unweighted_deficit_hours": deficit,
        })
    for contribution in contributions:
        contribution["equal_weight_wsdh_contribution"] = (
            contribution["unweighted_deficit_hours"] / Fraction(len(windows))
        )
        contribution["share_of_total_unweighted_deficit"] = (
            contribution["unweighted_deficit_hours"] / total_unweighted
            if total_unweighted else Fraction(0)
        )
    return contributions, total_unweighted


COMMON_FIELDS = [
    "case",
    "threshold",
    "included_cohorts",
    "omitted_cohort",
    "test_window_minutes",
    "minimum_availability_index",
    "time_below_threshold_minutes",
    "final_recovery_minutes",
    "recovery_observed",
    "right_censored",
    "wsdh_hours",
    "note",
]


def _write_csv(name, fieldnames, rows):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, name)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _metric_row(case, threshold, included, omitted, metrics, note):
    return {
        "case": case,
        "threshold": fmt10(threshold),
        "included_cohorts": ",".join(included),
        "omitted_cohort": omitted,
        "test_window_minutes": WINDOW_MINUTES,
        "minimum_availability_index": fmt10(metrics.minimum_availability_index),
        "time_below_threshold_minutes": metrics.time_below_threshold_minutes,
        "final_recovery_minutes": (
            "" if metrics.final_recovery_minutes is None
            else metrics.final_recovery_minutes
        ),
        "recovery_observed": str(metrics.recovery_observed).lower(),
        "right_censored": str(metrics.right_censored).lower(),
        "wsdh_hours": fmt10(metrics.wsdh_hours),
        "note": note,
    }


def _show(label, metrics):
    if metrics.final_recovery_minutes is None:
        recovery = f"not observed (right-censored at {WINDOW_MINUTES} min)"
    else:
        recovery = f"{metrics.final_recovery_minutes} min"
    print(
        f"{label:34s} minimum={fmt10(metrics.minimum_availability_index)}  "
        f"below={metrics.time_below_threshold_minutes:5d} min  "
        f"recovery={recovery}  WSDH={fmt10(metrics.wsdh_hours)} h"
    )


def main():
    rows = load_cohorts()
    selected = included_rows(rows)
    included_ids = [row["cohort_id"].strip() for row in selected]
    origin = window_origin(selected)
    all_windows = build_windows(selected, origin)

    baseline_metrics = compute_metrics(
        all_windows, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES
    )
    _write_csv(
        "main_metrics.csv",
        COMMON_FIELDS,
        [_metric_row(
            "baseline",
            ILLUSTRATIVE_THRESHOLD,
            included_ids,
            "",
            baseline_metrics,
            "six numerical cohorts, equal weights, 1-min step, threshold 0.80",
        )],
    )

    threshold_cases = []
    for label, threshold in (
        ("0.70", Fraction(7, 10)),
        ("0.80", Fraction(8, 10)),
        ("0.90", Fraction(9, 10)),
    ):
        metrics = compute_metrics(all_windows, threshold, WINDOW_MINUTES)
        threshold_cases.append((label, threshold, metrics))
    _write_csv(
        "threshold_sensitivity.csv",
        COMMON_FIELDS,
        [_metric_row(
            f"threshold_{label}",
            threshold,
            included_ids,
            "",
            metrics,
            "WSDH is independent of the passing threshold",
        ) for label, threshold, metrics in threshold_cases],
    )

    leave_one_out_cases = []
    for omitted in included_ids:
        subset = [window for window in all_windows if window[0] != omitted]
        metrics = compute_metrics(subset, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES)
        leave_one_out_cases.append((omitted, subset, metrics))
    _write_csv(
        "leave_one_out.csv",
        COMMON_FIELDS,
        [_metric_row(
            f"omit_{omitted}",
            ILLUSTRATIVE_THRESHOLD,
            [window[0] for window in subset],
            omitted,
            metrics,
            "equal weights renormalized; selection sensitivity, not business weights",
        ) for omitted, subset, metrics in leave_one_out_cases],
    )

    filestore = next(row for row in rows if row["cohort_id"].strip() == "FST")
    filestore_fraction = available_fraction(filestore)
    filestore_start = _offset(_parse_dt(filestore["impact_start_utc"]), origin)
    filestore_reported_end = _offset(
        _parse_dt(filestore["impact_end_utc"]), origin
    )
    filestore_cases = [
        (
            "filestore_reported_timestamps",
            all_windows + [(
                "FST", filestore_fraction, filestore_start, filestore_reported_end
            )],
            "sensitivity only: Filestore 0.55 for 905 min (reported timestamps)",
        ),
        (
            "filestore_stated_duration",
            all_windows + [(
                "FST", filestore_fraction, filestore_start, filestore_start + 630
            )],
            "sensitivity only: Filestore 0.55 for 630 min (stated duration)",
        ),
    ]
    filestore_results = [
        (name, windows, note,
         compute_metrics(windows, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES))
        for name, windows, note in filestore_cases
    ]
    _write_csv(
        "filestore_sensitivity.csv",
        COMMON_FIELDS,
        [_metric_row(
            name,
            ILLUSTRATIVE_THRESHOLD,
            [window[0] for window in windows],
            "",
            metrics,
            note,
        ) for name, windows, note, metrics in filestore_results],
    )

    contributions, total_unweighted = cohort_contributions(rows)
    contribution_fields = [
        "cohort_id",
        "duration_minutes",
        "available_fraction",
        "unweighted_deficit_hours",
        "equal_weight_wsdh_contribution",
        "share_of_total_unweighted_deficit",
    ]
    _write_csv(
        "cohort_contributions.csv",
        contribution_fields,
        [{
            "cohort_id": item["cohort_id"],
            "duration_minutes": item["duration_minutes"],
            "available_fraction": fmt10(item["available_fraction"]),
            "unweighted_deficit_hours": fmt10(item["unweighted_deficit_hours"]),
            "equal_weight_wsdh_contribution": fmt10(
                item["equal_weight_wsdh_contribution"]
            ),
            "share_of_total_unweighted_deficit": fmt10(
                item["share_of_total_unweighted_deficit"]
            ),
        } for item in contributions],
    )

    print("Availability-index robustness analysis")
    print(f"test window = {WINDOW_MINUTES} min; cohorts = {','.join(included_ids)}")
    print("-" * 112)
    _show("A. baseline (threshold 0.80)", baseline_metrics)
    print("-" * 112)
    for label, _, metrics in threshold_cases:
        _show(f"B. threshold {label}", metrics)
    print("-" * 112)
    for omitted, _, metrics in leave_one_out_cases:
        _show(f"C. omit {omitted}", metrics)
    print("-" * 112)
    for name, _, _, metrics in filestore_results:
        _show(f"D. {name}", metrics)
    print("-" * 112)
    print(f"E. unweighted total deficit = {fmt10(total_unweighted)} h")
    for item in contributions:
        print(
            f"    {item['cohort_id']:6s} dur={item['duration_minutes']:5d} min "
            f"deficit={fmt10(item['unweighted_deficit_hours'])} h "
            f"share={fmt10(item['share_of_total_unweighted_deficit'])}"
        )

    cohort_wsdh = sum(
        item["equal_weight_wsdh_contribution"] for item in contributions
    )
    print("-" * 112)
    print(
        f"self-check: minute-level WSDH = {fmt10(baseline_metrics.wsdh_hours)} h; "
        f"cohort-level WSDH = {fmt10(cohort_wsdh)} h; "
        f"equal = {baseline_metrics.wsdh_hours == cohort_wsdh}"
    )
    print("\nWrote results/", ", ".join(sorted(os.listdir(RESULTS_DIR))))


if __name__ == "__main__":
    main()
