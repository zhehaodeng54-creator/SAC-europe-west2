# Summary metrics

| Metric | Result |
|---|---:|
| Minimum availability index | **0.7078**, from 10:06 to 13:24 PDT |
| Minimum cohort fractions | BT 0.300; GKE 0.430; VPC 0.6366; CS 0.860; CT 0.940; CSch 0.940 |
| Time below 0.80 | **720 min = 12.0 h** |
| Final within-window recovery | **865 min = 14 h 25 min**, at 21:30 PDT |
| WSDH | **4.121 h** |

## Cohort-level service-deficit hours

| Cohort | Unweighted service-deficit hours |
|---|---:|
| BT | 13.475 h |
| GKE | 6.840 h |
| VPC | 3.791 h |
| CS | 0.224 h |
| CT | 0.199 h |
| CSch | 0.199 h |

The unweighted total is 24.728 h. Multiplication by the equal weight `1/6` gives
4.121 h, identical to the aggregate-index integral.

Rounded reporting values are 0.708, 12.0 h, 14 h 25 min, and 4.12 h.
