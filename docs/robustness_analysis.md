# Robustness analysis

This document accompanies `code/availability_index_robustness.py` and
`code/test_availability_index_robustness.py`.

## Purpose and fixed inputs

The analysis tests sensitivity to the illustrative threshold, cohort selection, and
the two conflicting Filestore time readings. It does not validate a threshold, derive
business weights, or measure workload-level delivery.

| Input | Baseline value |
|---|---|
| Cohorts | CS, BT, CT, CSch, GKE, VPC |
| Available fractions | 0.86, 0.30, 0.94, 0.94, 0.43, and 2234/3509 |
| Weights | Equal, renormalized when the cohort set changes |
| Observation window | 1,155 min |
| Time step | One minute |
| Interval convention | Left-closed, right-open `[start, end)` |
| Illustrative threshold | 0.80 |

Inputs are read from `data/service_cohorts.csv` and calculated with
exact rational arithmetic.

## Threshold sensitivity

| Threshold | Minimum index | Time below threshold | Final within-window recovery | WSDH |
|---:|---:|---:|---:|---:|
| 0.70 | 0.7077747696 | 0 min | 0 min | 4.1213276812 h |
| 0.80 | 0.7077747696 | 720 min | 865 min | 4.1213276812 h |
| 0.90 | 0.7077747696 | 1,155 min | Not observed | 4.1213276812 h |

The minimum and WSDH do not depend on the passing threshold. At 0.90, the index is
below threshold at the end of the fixed observation window. Recovery is therefore
right-censored and must not be reported as occurring at 1,155 minutes.

## Leave-one-cohort-out analysis

| Omitted cohort | Minimum index | Time below 0.80 | Final within-window recovery | WSDH |
|---|---:|---:|---:|---:|
| CS | 0.6493297236 | 720 min | 865 min | 4.9007932174 h |
| BT | 0.7893297236 | 198 min | 379 min | 2.2505932174 h |
| CT | 0.6613297236 | 720 min | 865 min | 4.9057932174 h |
| CSch | 0.6613297236 | 720 min | 865 min | 4.9057932174 h |
| GKE | 0.7633297236 | 626 min | 807 min | 3.5775932174 h |
| VPC | 0.7220000000 | 720 min | 865 min | 4.1874000000 h |

Omitting BT produces the largest change because its reported 0.30 available fraction
spans the full observation window. These cases change both the cohort set and the
equal-weight denominator, so they describe selection sensitivity only.

## Filestore time readings

The report's Filestore timestamps imply 905 minutes, while its text states 630 minutes.
Filestore remains excluded from the baseline; both readings are shown as seven-cohort
sensitivity cases with a reported available fraction of 0.55.

| Reading | Minimum index | Time below 0.80 | Final within-window recovery | WSDH |
|---|---:|---:|---:|---:|
| Reported timestamps, 905 min | 0.6852355168 | 685 min | 865 min | 4.5022094410 h |
| Stated duration, 630 min | 0.6852355168 | 630 min | 810 min | 4.2075665839 h |

## Cohort contributions

| Cohort | Duration | Available fraction | Unweighted deficit | Equal-weight WSDH contribution | Share |
|---|---:|---:|---:|---:|---:|
| CS | 96 min | 0.86 | 0.2240 h | 0.0373 h | 0.91% |
| BT | 1,155 min | 0.30 | 13.4750 h | 2.2458 h | 54.49% |
| CT | 199 min | 0.94 | 0.1990 h | 0.0332 h | 0.80% |
| CSch | 199 min | 0.94 | 0.1990 h | 0.0332 h | 0.80% |
| GKE | 720 min | 0.43 | 6.8400 h | 1.1400 h | 27.66% |
| VPC | 626 min | 0.6366486178 | 3.7910 h | 0.6318 h | 15.33% |
| Total | | | 24.7280 h | 4.1213 h | 100% |

BT and GKE account for approximately 82.2% of the unweighted deficit. This is a
mechanical consequence of the reported fractions and durations, not a ranking of
commercial or social importance.

## Interpretation limits

The analysis establishes arithmetic reproducibility and sensitivity. It does not
establish predictive validity, threshold validity, service criticality, provider-wide
resilience, electrical or cooling performance, or planning credit. The aggregate is
an availability-only normalized index built from heterogeneous public service records.
