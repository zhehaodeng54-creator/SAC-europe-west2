#!/usr/bin/env python3
"""Reproduce the baseline normalized service-availability calculation."""

import datetime
from fractions import Fraction

PDT = datetime.timezone(datetime.timedelta(hours=-7))


def pdt(year, month, day, hour, minute):
    return datetime.datetime(year, month, day, hour, minute, tzinfo=PDT)


# Verified from https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2
# Values are reported available shares during their respective service windows.
COHORTS = [
    ("CS", Fraction(86, 100), pdt(2022, 7, 19, 7, 18), pdt(2022, 7, 19, 8, 54)),
    ("BT", Fraction(30, 100), pdt(2022, 7, 19, 7, 5), pdt(2022, 7, 20, 2, 20)),
    ("CT", Fraction(94, 100), pdt(2022, 7, 19, 10, 5), pdt(2022, 7, 19, 13, 24)),
    ("CSch", Fraction(94, 100), pdt(2022, 7, 19, 10, 5), pdt(2022, 7, 19, 13, 24)),
    ("GKE", Fraction(43, 100), pdt(2022, 7, 19, 9, 30), pdt(2022, 7, 19, 21, 30)),
    ("VPC", 1 - Fraction(1275, 3509), pdt(2022, 7, 19, 10, 6), pdt(2022, 7, 19, 20, 32)),
]
WEIGHT = Fraction(1, 6)
THRESHOLD = Fraction(8, 10)
START = min(cohort[2] for cohort in COHORTS)
END = max(cohort[3] for cohort in COHORTS)
WINDOW_MINUTES = int((END - START).total_seconds() // 60)


def main():
    series = []
    for minute in range(WINDOW_MINUTES):
        moment = START + datetime.timedelta(minutes=minute)
        fractions = [
            available if start <= moment < end else Fraction(1)
            for _, available, start, end in COHORTS
        ]
        series.append(sum(fractions) * WEIGHT)

    minimum_index = min(series)
    below = sum(value < THRESHOLD for value in series)
    below_positions = [i for i, value in enumerate(series) if value < THRESHOLD]
    recovery = 0 if not below_positions else below_positions[-1] + 1
    if below_positions and below_positions[-1] == WINDOW_MINUTES - 1:
        recovery = None
    wsdh = sum(Fraction(1) - value for value in series) / Fraction(60)

    print("test_window_minutes =", WINDOW_MINUTES)
    print("minimum_availability_index =", float(minimum_index))
    print("time_below_0.80_minutes =", below, "=", below / 60, "h")
    print("final_recovery_minutes =", recovery)
    print("WSDH_hours =", float(wsdh))

    events = []
    for cohort_id, _, start, end in COHORTS:
        events.append((int((start - START).total_seconds() // 60), +1, cohort_id))
        events.append((int((end - START).total_seconds() // 60), -1, cohort_id))
    points = sorted({0, WINDOW_MINUTES, *(event[0] for event in events)})
    by_id = {cohort[0]: cohort[1] for cohort in COHORTS}
    active = set()
    segments = []
    for left, right in zip(points, points[1:]):
        for moment, direction, cohort_id in events:
            if moment == left:
                if direction == +1:
                    active.add(cohort_id)
                else:
                    active.discard(cohort_id)
        fractions = [
            by_id[cohort_id] if cohort_id in active else Fraction(1)
            for cohort_id in by_id
        ]
        segments.append((left, right, sum(fractions) * WEIGHT))

    print("\nsegments (start,end,availability_index):")
    for left, right, value in segments:
        print("  [%4d,%4d)  %.6f" % (left, right, float(value)))
    piecewise_wsdh = sum(
        (Fraction(1) - value) * Fraction(right - left, 60)
        for left, right, value in segments
    )
    print("piecewise minimum =", float(min(value for _, _, value in segments)))
    print(
        "piecewise below-threshold minutes =",
        sum(right - left for left, right, value in segments if value < THRESHOLD),
    )
    print("piecewise WSDH =", float(piecewise_wsdh))

    deficits = []
    for cohort_id, available, start, end in COHORTS:
        duration_hours = Fraction(int((end - start).total_seconds() // 60), 60)
        deficits.append((cohort_id, (Fraction(1) - available) * duration_hours))
    cohort_wsdh = sum(value for _, value in deficits) / Fraction(len(COHORTS))
    print("\ncohort-deficit WSDH =", float(cohort_wsdh), "== WSDH?", cohort_wsdh == wsdh)
    for cohort_id, value in deficits:
        print("  %s: %.4f service-deficit-hours" % (cohort_id, float(value)))


if __name__ == "__main__":
    main()
