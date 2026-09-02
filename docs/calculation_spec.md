# Calculation specification

The following rules were fixed before calculating the summary metrics.

1. The test window runs from the earliest impact start to the latest impact end among the six included cohorts: 19 July 2022 07:05 PDT to 20 July 2022 02:20 PDT, equivalent to 14:05 UTC to 09:20 UTC. Its duration is 1,155 min, or 19 h 15 min.
2. The time step is one minute.
3. Baseline demand `D_i^0(t)` is normalized to 1 per minute for every cohort.
4. Availability is the only service-level condition because the public report does not provide latency, error, or deadline-compliance data for the six numerical cohorts.
5. The delivered fraction `f_i(t)` equals the reported available fraction within the official impact window and equals 1 outside that window.
6. The six cohorts receive equal weights, `w_i = 1/6`.
7. The aggregate threshold is 0.80. This threshold is illustrative and is not a Google service-level objective or service-level agreement.
8. No essential-class threshold is assigned because the public report does not disclose business criticality.
9. The calculation does not infer customer request volumes, revenue, social value, AI workload attribution, migration strategy, or response policy.
10. Every interval is left-closed and right-open, `[start, end)`. The availability-only data do not describe backlog completion.

## Exclusion rules

- Vertex AI is excluded from numerical SAC because no affected or available fraction was reported. It remains background evidence only.
- Filestore is excluded from the main calculation because the reported start and end times conflict with the stated duration. Both time readings are retained in the sensitivity analysis in `verification.md`.

## Start-to-end duration cross-check

| Cohort | Duration from timestamps | Duration stated in report | Consistent? |
|---|---:|---:|---|
| CS | 96 min | 96 min | Yes |
| BT | 19 h 15 min | 19 h 15 min | Yes |
| CT | 3 h 19 min | 3 h 19 min | Yes |
| CSch | 3 h 19 min | 3 h 19 min | Yes |
| GKE | 12 h | approximately 12 h | Yes |
| VPC | 10 h 26 min | 10 h 26 min | Yes |
| Vertex AI | 5 h 11 min | 5 h 11 min | Yes |
| Filestore | 15 h 05 min | 10 h 30 min | No |
