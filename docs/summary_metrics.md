# Summary metrics

| Metric | Result |
|---|---:|
| Minimum SAC | **0.7078**, from 10:06 to 13:24 PDT |
| Minimum class-level delivered fractions | BT 0.300; GKE 0.430; VPC 0.6366; CS 0.860; CT 0.940; CSch 0.940 |
| Total time with SAC below 0.80 | **720 min = 12.0 h** |
| Time to sustained aggregate-threshold recovery, SAC at or above 0.80 without a later decline below it | **865 min = 14 h 25 min**, at 21:30 PDT when GKE nodes recovered |
| WSDH, `sum_t [1 - SAC(t)] delta_t` | **4.121 h** |

## Cohort-level service-deficit hours

Each cohort has weight `w_i = 1/6` in the aggregate.

| Cohort | Unweighted service-deficit hours, `(1 - f_i) x duration` |
|---|---:|
| BT | 13.475 h |
| GKE | 6.840 h |
| VPC | 3.791 h |
| CS | 0.224 h |
| CT | 0.199 h |
| CSch | 0.199 h |

The unweighted total is 24.728 h. Multiplying by `1/6` gives 4.121 h, equal to the aggregate SAC integral.

## Manuscript rounding

- Minimum SAC: 0.708
- Time below the illustrative 0.80 threshold: 12.0 h
- Sustained aggregate-threshold recovery: 14 h 25 min
- WSDH: 4.12 h

These are rounded displays of the verified calculation outputs, not altered results.
