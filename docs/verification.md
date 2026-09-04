# Independent arithmetic verification

The baseline was evaluated three ways with matching results.

| Method | Minimum index | Time below 0.80 | Final within-window recovery | WSDH |
|---|---:|---:|---:|---:|
| Event-boundary integration | 0.7078 | 720 min | 865 min | 4.1213 h |
| One-minute simulation | 0.7078 | 720 min | 865 min | 4.1213 h |
| Cohort-deficit integral | n/a | n/a | n/a | 4.1213 h |

The cohort identity is

```text
sum_t [1 - availability_index(t)] delta_t
= sum_i w_i (1 - f_i) duration_i
= 4.1213276812 h.
```

## Filestore consistency check

The reported timestamps run from 10:05 to 01:10 on the following day, which is 905
minutes. The same report states 630 minutes. The record is excluded from the baseline,
and both readings are retained as sensitivity cases.

## Quality-control checklist

1. All numerical available fractions lie in `[0,1]`.
2. Exact VPC counts produce `2234/3509` available.
3. Equal weights sum to one in each case.
4. The aggregate index lies in `[0,1]` at every minute.
5. All durations are non-negative.
6. Minute-level and cohort-level WSDH agree exactly.
7. The nine baseline intervals cover 1,155 minutes without gaps or overlaps.
8. Approximate source values remain marked approximate.
9. The Filestore duration conflict is retained rather than silently resolved.
10. A source row without a numerical available fraction is not imputed or calculated.
11. A below-threshold series at the final minute is reported as right-censored.

## Automated verification

The 20-test suite covers fixed baseline and sensitivity values, CSV structure and
censoring serialization, exact VPC counts, missing-value handling, interval endpoints,
threshold equality, final-minute recovery, and independent event-boundary integration.
The hard-coded baseline inputs are also checked against the canonical CSV.
The export schema uses `final_recovery_minutes`; contextual evidence is excluded from
the numerical cohort set.

These checks establish correctness for the supplied reconstruction and tested boundary
cases. They do not establish the accuracy of the source report or general validity for
other incidents.
