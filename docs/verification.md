# Independent arithmetic verification

The calculation was run two ways, with matching results.

| Method | Minimum SAC | Time below 0.80 | Sustained recovery | WSDH, h |
|---|---:|---:|---:|---:|
| Event-boundary integration | 0.7078 | 720 min | 865 min | 4.1213 |
| One-minute discrete simulation | 0.7078 | 720 min | 865 min | 4.1213 |
| Agreement | Yes | Yes | Yes | Yes |

WSDH was also recomputed from cohort-level deficit integrals: `sum_i w_i (1 - f_i) duration = 4.1213 h`. This equals the aggregate SAC integral.

## Filestore inconsistency and sensitivity

The reported Filestore timestamps run from 10:05 to 01:10 on the following day, a duration of 15 h 05 min. The same report states a duration of 10 h 30 min. Because these statements conflict, Filestore is excluded from the main six-cohort calculation.

For sensitivity only, Filestore is assigned an available fraction of 0.55 and added as a seventh equally weighted cohort.

| Filestore interpretation | Minimum SAC | Time below 0.80 | WSDH, h |
|---|---:|---:|---:|
| A: reported timestamps, 10:05-01:10, 15 h 05 min | 0.6852 | 685 min = 11.42 h | 4.502 |
| B: stated duration, 10 h 30 min, ending at 20:35 | 0.6852 | 630 min = 10.50 h | 4.208 |

The two readings change the duration below threshold and WSDH but not the minimum SAC, because both include the minimum interval from 10:06 to 13:24.

## Bigtable and GKE concentration sensitivity

BT and GKE contribute 13.475 h and 6.840 h, respectively, to the unweighted total of 24.728 cohort-level service-deficit hours. Together they account for approximately 82% of the WSDH numerator. This concentration follows from reading the report as approximately 70% of BT instances fully unavailable, leaving 0.30 available, and 57% of GKE nodes unavailable, leaving 0.43 available, during their reported windows.

If either statement were instead interpreted as partial degradation within the affected population, the corresponding available fraction would be higher. Holding all other inputs fixed, its cohort-level deficit, aggregate WSDH, and SAC reduction would be smaller. No alternative numerical value is calculated because the official report does not quantify a partial-degradation fraction for these cohorts.

## Quality-control checklist

1. Every reported available fraction lies in `[0, 1]`: passed.
2. Impacted and available fractions are complementary: passed for CS, BT, CT, CSch, GKE, and VPC.
3. The full VPC count ratio is shown: `1275/3509` affected and `2234/3509` available.
4. The six weights sum to 1 in every interval: `1/6 x 6`.
5. SAC remains in `[0, 1]`: passed.
6. WSDH agrees between the cohort-deficit and aggregate-SAC integrals: passed.
7. The nine intervals cover the complete 1,155-minute test window without a gap or overlap: `13 + 96 + 36 + 35 + 1 + 198 + 428 + 58 + 290 = 1155`.
8. Approximate source values remain identified as approximate: passed for CS, BT, and the VPC report text.
9. The Filestore duration inconsistency is explicitly reported: passed.
10. Vertex AI remains background evidence, and no numerical affected fraction is imputed: passed.
