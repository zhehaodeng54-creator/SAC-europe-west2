# Piecewise results

Minute offsets are measured from 07:05 PDT on 19 July 2022. Fractions are listed in
cohort order CS, BT, CT, CSch, GKE, and VPC.

| Interval, min | Interval, PDT | Active cohorts | f_CS | f_BT | f_CT | f_CSch | f_GKE | f_VPC | Availability index |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `[0, 13)` | 07:05-07:18 | BT | 1.000 | 0.300 | 1.000 | 1.000 | 1.000 | 1.000 | 0.8833 |
| `[13, 109)` | 07:18-08:54 | BT, CS | 0.860 | 0.300 | 1.000 | 1.000 | 1.000 | 1.000 | 0.8600 |
| `[109, 145)` | 08:54-09:30 | BT | 1.000 | 0.300 | 1.000 | 1.000 | 1.000 | 1.000 | 0.8833 |
| `[145, 180)` | 09:30-10:05 | BT, GKE | 1.000 | 0.300 | 1.000 | 1.000 | 0.430 | 1.000 | 0.7883 |
| `[180, 181)` | 10:05-10:06 | BT, GKE, CT, CSch | 1.000 | 0.300 | 0.940 | 0.940 | 0.430 | 1.000 | 0.7683 |
| `[181, 379)` | 10:06-13:24 | BT, GKE, CT, CSch, VPC | 1.000 | 0.300 | 0.940 | 0.940 | 0.430 | 0.6366 | **0.7078** |
| `[379, 807)` | 13:24-20:32 | BT, GKE, VPC | 1.000 | 0.300 | 1.000 | 1.000 | 0.430 | 0.6366 | 0.7278 |
| `[807, 865)` | 20:32-21:30 | BT, GKE | 1.000 | 0.300 | 1.000 | 1.000 | 0.430 | 1.000 | 0.7883 |
| `[865, 1155)` | 21:30-02:20 | BT | 1.000 | 0.300 | 1.000 | 1.000 | 1.000 | 1.000 | 0.8833 |

Outside its reported impact window, a cohort has `f_i(t) = 1`. The equal-weight index
is the arithmetic mean of the six cohort fractions.
