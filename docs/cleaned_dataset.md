# Cleaned dataset

| cohort_id | service_name | region_or_zone | reported_population | reported_impacted_count | reported_impacted_fraction | reported_available_fraction | impact_start_original | impact_end_original | source_timezone | impact_start_utc | impact_end_utc | duration_minutes | approximate_value | inclusion_status | exclusion_reason | calculation_assumption |
|---|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|
| CS | Cloud Storage ReadObject, regional buckets | europe-west2 | n/a, 24% of projects affected | n/a | 0.14 | 0.86 | 2022-07-19 07:18 | 2022-07-19 08:54 | US/Pacific, PDT, UTC-7 | 2022-07-19 14:18 | 2022-07-19 15:54 | 96 | yes | included | | availability = 0.86 within window |
| BT | Unreplicated Bigtable instances | europe-west2-a | n/a | n/a | 0.70 | 0.30 | 2022-07-19 07:05 | 2022-07-20 02:20 | US/Pacific, PDT, UTC-7 | 2022-07-19 14:05 | 2022-07-20 09:20 | 1155 | yes | included | | approximately 70% fully unavailable, therefore 30% available |
| CT | Cloud Tasks projects | europe-west2 | n/a | n/a | 0.06 | 0.94 | 2022-07-19 10:05 | 2022-07-19 13:24 | US/Pacific, PDT, UTC-7 | 2022-07-19 17:05 | 2022-07-19 20:24 | 199 | no | included | | availability = 0.94 within window |
| CSch | Cloud Scheduler projects | europe-west2 | n/a | n/a | 0.06 | 0.94 | 2022-07-19 10:05 | 2022-07-19 13:24 | US/Pacific, PDT, UTC-7 | 2022-07-19 17:05 | 2022-07-19 20:24 | 199 | no | included | | availability = 0.94 within window |
| GKE | GKE regional and zonal cluster nodes | europe-west2-a | n/a | n/a | 0.57 | 0.43 | 2022-07-19 09:30 | 2022-07-19 21:30 | US/Pacific, PDT, UTC-7 | 2022-07-19 16:30 | 2022-07-20 04:30 | 720 | no | included | | 57% unavailable, therefore 43% available |
| VPC | Reachable VPC virtual machines | europe-west2-a | 3509 | 1275 | 1275/3509 = 0.36335 | 2234/3509 = 0.63665 | 2022-07-19 10:06 | 2022-07-19 20:32 | US/Pacific, PDT, UTC-7 | 2022-07-19 17:06 | 2022-07-20 03:32 | 626 | yes | included | | exact counts used; report text says approximately 35% |
| FST | Cloud Filestore | europe-west2-a | n/a | n/a | 0.45 | 0.55 | 2022-07-19 10:05 | 2022-07-20 01:10 | US/Pacific, PDT, UTC-7 | 2022-07-19 17:05 | 2022-07-20 08:10 | 905 | no | excluded from main calculation | stated times imply 15 h 05 min, but the report text says 10 h 30 min | sensitivity analysis uses both time readings |

The machine-readable version of this table is `data/service_cohorts.csv`.

## Field interpretation

- `reported_impacted_fraction` and `reported_available_fraction` are complements and sum to 1.
- CS: the report states that availability fell to approximately 86%. The statement that 24% of customer projects were affected describes breadth of impact and is not the complement of the available fraction.
- BT: approximately 70% of instances were fully unavailable. Cohort availability is therefore 0.30, calculated as `0.70 x 0 + 0.30 x 1`.
- VPC: the report describes approximately 35% as affected and also gives exact counts. The calculation uses the full count ratio: impacted `1275/3509 = 0.36335`, available `2234/3509 = 0.63665`.
- Filestore: the stated start and end times imply 15 h 05 min, whereas the report text states 10 h 30 min. It is excluded from the main calculation and retained only for the two sensitivity readings reported in `verification.md`.

## Time conversion

All source times are US/Pacific. In July 2022, this was Pacific Daylight Time, UTC-7. Cross-date end times are handled explicitly: BT ends at 02:20 PDT on 20 July, which is 09:20 UTC; GKE ends at 21:30 PDT on 19 July, which is 04:30 UTC on 20 July; VPC ends at 20:32 PDT on 19 July, which is 03:32 UTC on 20 July. All intervals are left-closed and right-open, `[start, end)`.
