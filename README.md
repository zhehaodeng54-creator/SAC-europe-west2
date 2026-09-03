# Scenario-Available Compute Reconstruction for Google Cloud europe-west2

This repository reproduces a scenario-available compute (SAC) calculation for the Google Cloud europe-west2 incident of 19-20 July 2022. The exercise shows that SAC can be calculated from a public incident report. It does not test predictive validity or measure AI workload delivery.

## Key results

The reconstruction uses six normalized service cohorts, an availability-only service-level condition, equal weights, one-minute time steps, and an illustrative aggregate threshold of 0.80.

| Metric | Result |
|---|---:|
| Test window | 1,155 min = 19 h 15 min |
| Minimum SAC | 0.7077747696... = 0.708 when rounded for the manuscript |
| Time with SAC below 0.80 | 720 min = 12.0 h |
| Sustained aggregate-threshold recovery | 865 min = 14 h 25 min |
| Weighted service-deficit hours, WSDH | 4.1213276812... h = 4.12 h when rounded for the manuscript |

The six included cohorts and their available fractions within the reported impact windows are:

| Cohort | Available fraction used |
|---|---:|
| Cloud Storage ReadObject, CS | approximately 0.86 |
| Unreplicated Bigtable, BT | 0.30, derived from approximately 70% fully unavailable |
| Cloud Tasks, CT | 0.94 |
| Cloud Scheduler, CSch | 0.94 |
| Google Kubernetes Engine nodes, GKE | 0.43 |
| Reachable Virtual Private Cloud virtual machines, VPC | 2234/3509 = 0.63665; the report describes the affected share as approximately 35% |

## Reproduce the calculation

Python 3 is required. The script uses only the Python standard library.

```bash
python3 code/sac_calc.py
```

Running the script produces a one-minute simulation and an event-boundary calculation. It then computes WSDH again from the cohort-level deficit hours. The three results should agree. The verified cohort records are in `data/sac_cohorts.csv`. To preserve the audited calculation, the script also stores those fixed inputs directly in the code.

## Repository contents

```text
SAC-europe-west2/
|-- README.md
|-- LICENSE
|-- .gitignore
|-- data/
|   `-- sac_cohorts.csv
|-- code/
|   `-- sac_calc.py
`-- docs/
    |-- source_audit.md
    |-- cleaned_dataset.md
    |-- calculation_spec.md
    |-- piecewise_results.md
    |-- summary_metrics.md
    `-- verification.md
```

## Framework and interpretation boundaries

For cohort or workload class `i` at time `t`:

- `D_i^0(t)` is baseline demand. It is normalized to 1 per minute for every included cohort in this reconstruction.
- `Y_i(t)` is the amount delivered within the service-level objective under scenario `s` and response policy `r`.
- The class-level delivered fraction is `f_i(t) = min{1, Y_i(t) / D_i^0(t)}`.
- `SAC(t) = sum_i w_i f_i(t) / sum_i w_i`. Here, every `w_i` equals `1/6`.
- `WSDH = sum_t [1 - SAC(t)] delta_t`, where `delta_t` is measured in hours.

Interpret the results within these limits:

1. This is a retrospective public-data demonstration.
2. It establishes SAC calculability, not predictive validity.
3. The six objects are normalized service cohorts, not AI workloads.
4. Equal weights do not imply equal business or social value across the six services.
5. Availability alone does not establish compliance with latency, error, deadline, checkpoint, or recovery objectives.
6. The public report does not disclose customer demand, AI workload attribution, a formal response policy, or business criticality.
7. The results cannot be used to evaluate Google-wide resilience, compare Google with another provider, or benchmark providers.
8. A formal SAC assessment for an AI data center would require workload-level demand, latency, error, deadline, checkpoint, and support-path telemetry.
9. Because the cohorts mix reported request, project, instance, node, and virtual-machine availability, the aggregate is an illustrative normalized index rather than a measurement of workload-level compute delivery.

The 0.80 aggregate threshold is illustrative. It is not a Google service-level objective or service-level agreement. Approximate source values remain approximate, and no confidence intervals are inferred. The cohort set, weights, test window, and endpoint rules were not adjusted to obtain a preferred result.

## Data availability

The sole primary source is the official Google Cloud incident report, *Multiple Cloud products experiencing elevated error rates, latencies or service unavailability in europe-west2*, incident `fmEL9i2fArADKawkZAa2`, posted 29 July 2022 and accessed 2 September 2026:

https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2

The repository contains the cleaned cohort table, calculation rules, Python script, piecewise results, summary metrics, and arithmetic checks. Every numerical input traces to the official report. Missing service fractions and durations were left missing rather than imputed.

## License

The repository is released under the MIT License. See `LICENSE`.
