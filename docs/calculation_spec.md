# Calculation specification

1. The observation window runs from the earliest start to the latest end among the six
   baseline cohorts: 19 July 2022 07:05 PDT to 20 July 2022 02:20 PDT, or 1,155 minutes.
2. The time step is one minute.
3. Each cohort is normalized to an unaffected available fraction of 1.
4. Availability is the only evaluated condition because the report does not supply a
   common numerical latency, deadline, or backlog-completion series.
5. Within a reported impact window, `f_i(t)` equals the reported available fraction;
   outside it, `f_i(t) = 1`.
6. The six baseline cohorts receive equal weights, `w_i = 1/6`.
7. The aggregate index is `sum_i w_i f_i(t) / sum_i w_i`.
8. The illustrative threshold is 0.80. It is not a Google objective or agreement.
9. No essential or critical cohort is designated because the public report does not
   disclose business criticality.
10. WSDH is `sum_t [1 - availability_index(t)] delta_t`, with `delta_t = 1/60 h`.
11. Intervals are left-closed and right-open, `[start, end)`.
12. Missing fractions are not imputed, and conflicting durations are not silently
    resolved.

## Exclusion rules

- Vertex AI online prediction is retained only as contextual evidence in `source_audit.md`.
  It is absent from the numerical CSV because no affected or available fraction was
  published. No value is imputed.
- Filestore is excluded from the baseline because its timestamps and stated duration
  conflict. Both readings are retained as sensitivity cases.

## Duration cross-check

| Cohort | Duration from timestamps | Duration stated | Consistent? |
|---|---:|---:|---|
| CS | 96 min | 96 min | Yes |
| BT | 19 h 15 min | 19 h 15 min | Yes |
| CT | 3 h 19 min | 3 h 19 min | Yes |
| CSch | 3 h 19 min | 3 h 19 min | Yes |
| GKE | 12 h | approximately 12 h | Yes |
| VPC | 10 h 26 min | 10 h 26 min | Yes |
| Filestore | 15 h 05 min | 10 h 30 min | No |

## Recovery and censoring

Final within-window recovery is the earliest minute from which the index remains at or
above threshold through the end of observation. If
the final observed minute remains below threshold, recovery is not observed. Output
tables then leave `final_recovery_minutes` blank and set `right_censored=true`.

This is a retrospective stays-above-through-end rule, not a predeclared recovery-hold
period. Zero denotes passing throughout the window. The exclusive window endpoint is
not a post-recovery observation and cannot establish recovery beyond it.
