#!/usr/bin/env python3
"""Unit tests for ``availability_index_robustness.py``."""

import os
import csv
import io
import datetime
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from availability_index_robustness import (  # noqa: E402
    ILLUSTRATIVE_THRESHOLD,
    COMMON_FIELDS,
    WINDOW_MINUTES,
    _offset,
    _parse_dt,
    _metric_row,
    availability_series,
    available_fraction,
    build_windows,
    cohort_contributions,
    compute_metrics,
    included_rows,
    load_cohorts,
    window_origin,
)


def fmt(value):
    return format(float(value), ".10f")


class TestAvailabilityIndexRobustness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_cohorts()
        cls.included = included_rows(cls.rows)
        cls.ids = [row["cohort_id"].strip() for row in cls.included]
        cls.origin = window_origin(cls.included)
        cls.windows = build_windows(cls.included, cls.origin)

    def test_baseline(self):
        metrics = compute_metrics(
            self.windows, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES
        )
        self.assertEqual(fmt(metrics.minimum_availability_index), "0.7077747696")
        self.assertEqual(metrics.time_below_threshold_minutes, 720)
        self.assertEqual(metrics.final_recovery_minutes, 865)
        self.assertTrue(metrics.recovery_observed)
        self.assertFalse(metrics.right_censored)
        self.assertEqual(fmt(metrics.wsdh_hours), "4.1213276812")

    def test_threshold_sensitivity_and_censoring(self):
        expected = {
            Fraction(7, 10): (0, 0, True, False),
            Fraction(8, 10): (720, 865, True, False),
            Fraction(9, 10): (1155, None, False, True),
        }
        for threshold, values in expected.items():
            below, recovery, observed, censored = values
            metrics = compute_metrics(self.windows, threshold, WINDOW_MINUTES)
            self.assertEqual(fmt(metrics.minimum_availability_index), "0.7077747696")
            self.assertEqual(metrics.time_below_threshold_minutes, below)
            self.assertEqual(metrics.final_recovery_minutes, recovery)
            self.assertEqual(metrics.recovery_observed, observed)
            self.assertEqual(metrics.right_censored, censored)
            self.assertEqual(fmt(metrics.wsdh_hours), "4.1213276812")

    def test_leave_one_out(self):
        expected = {
            "CS": ("0.6493297236", 720, 865, "4.9007932174"),
            "BT": ("0.7893297236", 198, 379, "2.2505932174"),
            "CT": ("0.6613297236", 720, 865, "4.9057932174"),
            "CSch": ("0.6613297236", 720, 865, "4.9057932174"),
            "GKE": ("0.7633297236", 626, 807, "3.5775932174"),
            "VPC": ("0.7220000000", 720, 865, "4.1874000000"),
        }
        self.assertEqual(set(expected), set(self.ids))
        for omitted, values in expected.items():
            minimum, below, recovery, wsdh = values
            subset = [window for window in self.windows if window[0] != omitted]
            metrics = compute_metrics(subset, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES)
            self.assertEqual(fmt(metrics.minimum_availability_index), minimum, omitted)
            self.assertEqual(metrics.time_below_threshold_minutes, below, omitted)
            self.assertEqual(metrics.final_recovery_minutes, recovery, omitted)
            self.assertEqual(fmt(metrics.wsdh_hours), wsdh, omitted)

    def _filestore_cases(self):
        row = next(item for item in self.rows if item["cohort_id"].strip() == "FST")
        fraction = available_fraction(row)
        start = _offset(_parse_dt(row["impact_start_utc"]), self.origin)
        reported_end = _offset(_parse_dt(row["impact_end_utc"]), self.origin)
        return fraction, start, reported_end

    def test_filestore_durations(self):
        _, start, reported_end = self._filestore_cases()
        self.assertEqual(reported_end - start, 905)
        self.assertEqual(start, 180)
        self.assertEqual(start + 630, 810)

    def test_filestore_sensitivity_values(self):
        fraction, start, reported_end = self._filestore_cases()
        cases = [
            (
                self.windows + [("FST", fraction, start, reported_end)],
                "0.6852355168", 685, 865, "4.5022094410",
            ),
            (
                self.windows + [("FST", fraction, start, start + 630)],
                "0.6852355168", 630, 810, "4.2075665839",
            ),
        ]
        for windows, minimum, below, recovery, wsdh in cases:
            metrics = compute_metrics(windows, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES)
            self.assertEqual(fmt(metrics.minimum_availability_index), minimum)
            self.assertEqual(metrics.time_below_threshold_minutes, below)
            self.assertEqual(metrics.final_recovery_minutes, recovery)
            self.assertEqual(fmt(metrics.wsdh_hours), wsdh)

    def _all_cases(self):
        fraction, start, reported_end = self._filestore_cases()
        cases = {
            "baseline": self.windows,
            "filestore_reported": self.windows + [
                ("FST", fraction, start, reported_end)
            ],
            "filestore_stated": self.windows + [
                ("FST", fraction, start, start + 630)
            ],
        }
        for omitted in self.ids:
            cases[f"omit_{omitted}"] = [
                window for window in self.windows if window[0] != omitted
            ]
        return cases

    def test_index_within_unit_interval(self):
        for name, windows in self._all_cases().items():
            for minute, value in enumerate(availability_series(windows)):
                self.assertGreaterEqual(value, 0, f"{name} minute={minute}")
                self.assertLessEqual(value, 1, f"{name} minute={minute}")

    def test_durations_non_negative(self):
        for _, available, start, end in self.windows:
            self.assertGreaterEqual(end - start, 0)
            self.assertGreaterEqual(available, 0)
            self.assertLessEqual(available, 1)
        contributions, _ = cohort_contributions(self.rows)
        for item in contributions:
            self.assertGreaterEqual(item["duration_minutes"], 0)

    def test_wsdh_integral_equality(self):
        metrics = compute_metrics(
            self.windows, ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES
        )
        contributions, _ = cohort_contributions(self.rows)
        cohort_wsdh = sum(
            item["equal_weight_wsdh_contribution"] for item in contributions
        )
        self.assertEqual(metrics.wsdh_hours, cohort_wsdh)
        self.assertEqual(fmt(metrics.wsdh_hours), fmt(cohort_wsdh))

    def test_missing_fraction_is_not_imputed(self):
        row = dict(next(item for item in self.rows if item["cohort_id"].strip() == "FST"))
        row["cohort_id"] = "MISSING"
        row["reported_population"] = "n/a"
        row["reported_impacted_count"] = "n/a"
        row["reported_available_fraction"] = "n/a"
        self.assertIsNone(available_fraction(row))
        self.assertEqual(build_windows([row], self.origin), [])

    def test_exact_vpc_counts_used(self):
        row = next(item for item in self.rows if item["cohort_id"].strip() == "VPC")
        self.assertEqual(available_fraction(row), Fraction(2234, 3509))

    def test_empty_windows_rejected(self):
        with self.assertRaises(ValueError):
            compute_metrics([], ILLUSTRATIVE_THRESHOLD, WINDOW_MINUTES)

    def test_interval_end_is_excluded(self):
        series = availability_series([("TEST", Fraction(1, 2), 1, 3)], 4)
        self.assertEqual(series, [Fraction(1), Fraction(1, 2), Fraction(1, 2), Fraction(1)])

    def test_equal_to_threshold_passes(self):
        metrics = compute_metrics([("TEST", Fraction(4, 5), 0, 3)], Fraction(4, 5), 3)
        self.assertEqual(metrics.time_below_threshold_minutes, 0)
        self.assertEqual(metrics.final_recovery_minutes, 0)

    def test_final_minute_recovery_and_censoring(self):
        recovered = compute_metrics([("TEST", Fraction(0), 0, 2)], Fraction(1), 3)
        censored = compute_metrics([("TEST", Fraction(0), 0, 3)], Fraction(1), 3)
        self.assertEqual(recovered.final_recovery_minutes, 2)
        self.assertIsNone(censored.final_recovery_minutes)

    def test_censoring_csv_round_trip(self):
        metrics = compute_metrics(self.windows, Fraction(9, 10))
        row = _metric_row("threshold_0.90", Fraction(9, 10), self.ids, "", metrics, "")
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=COMMON_FIELDS)
        writer.writeheader()
        writer.writerow(row)
        buffer.seek(0)
        restored = next(csv.DictReader(buffer))
        self.assertEqual(restored["final_recovery_minutes"], "")
        self.assertEqual(restored["recovery_observed"], "false")
        self.assertEqual(restored["right_censored"], "true")

    def test_csv_schema_and_cohort_set(self):
        self.assertEqual(len(self.rows), 7)
        self.assertEqual(self.ids, ["CS", "BT", "CT", "CSch", "GKE", "VPC"])
        for row in self.rows:
            self.assertEqual(len(row), 17)
            self.assertNotIn(None, row)
            self.assertNotIn(None, row.values())

    def test_baseline_inputs_match_independent_script(self):
        from availability_index_calc import COHORTS
        for csv_window, fixed in zip(self.windows, COHORTS):
            cohort_id, available, start, end = fixed
            origin = self.origin.replace(tzinfo=datetime.timezone.utc)
            self.assertEqual(csv_window, (
                cohort_id, available,
                int((start - origin).total_seconds() // 60),
                int((end - origin).total_seconds() // 60),
            ))

    def test_event_integration_matches_minute_metrics(self):
        for name, windows in self._all_cases().items():
            points = sorted({0, WINDOW_MINUTES} | {
                boundary for _, _, start, end in windows for boundary in (start, end)
            })
            segments = []
            for left, right in zip(points, points[1:]):
                value = sum(
                    available if start <= left < end else Fraction(1)
                    for _, available, start, end in windows
                ) / len(windows)
                segments.append((left, right, value))
            below = sum(right - left for left, right, value in segments
                        if value < ILLUSTRATIVE_THRESHOLD)
            last_below_end = max((right for _, right, value in segments
                                  if value < ILLUSTRATIVE_THRESHOLD), default=0)
            recovery = None if last_below_end == WINDOW_MINUTES else last_below_end
            wsdh = sum((1 - value) * Fraction(right - left, 60)
                       for left, right, value in segments)
            metrics = compute_metrics(windows, ILLUSTRATIVE_THRESHOLD)
            self.assertEqual(metrics.minimum_availability_index,
                             min(value for _, _, value in segments), name)
            self.assertEqual(metrics.time_below_threshold_minutes, below, name)
            self.assertEqual(metrics.final_recovery_minutes, recovery, name)
            self.assertEqual(metrics.wsdh_hours, wsdh, name)


    def test_export_schema_uses_final_recovery_name(self):
        self.assertIn("final_recovery_minutes", COMMON_FIELDS)
        self.assertNotIn("sustained_recovery_minutes", COMMON_FIELDS)

    def test_contextual_record_is_not_a_numerical_cohort(self):
        ids = {row["cohort_id"].strip() for row in self.rows}
        self.assertEqual(ids, {"CS", "BT", "CT", "CSch", "GKE", "VPC", "FST"})
        self.assertNotIn("VAI", ids)


if __name__ == "__main__":
    unittest.main()
