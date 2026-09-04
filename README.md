# Availability-Only Service Reconstruction for Google Cloud europe-west2

This repository reconstructs a normalized service-availability index for six public
Google Cloud service records from the europe-west2 incident of 19-20 July 2022. It is
an auditable accounting example, not a measurement of workload-level compute delivery,
provider-wide resilience, or business impact.

The calculation uses the same weighted aggregation and service-deficit integral as the
accompanying manuscript. This repository deliberately uses availability-index
terminology because the public inputs are heterogeneous service-availability records.

## Baseline results

The baseline uses six numerical cohorts, equal weights, one-minute intervals, and an
illustrative aggregate threshold of 0.80.

| Metric | Result |
|---|---:|
| Observation window | 1,155 min = 19 h 15 min |
| Minimum availability index | 0.7077747696 = 0.708 when rounded |
| Time below 0.80 | 720 min = 12.0 h |
| Final within-window recovery | 865 min = 14 h 25 min |
| Weighted service-deficit hours, WSDH | 4.1213276812 h = 4.12 h when rounded |

The 0.80 threshold is illustrative. It is not a Google service-level objective or
service-level agreement.

## Reproduce and verify

Python 3.7 or later is required. The code uses only the standard library.

```bash
python code/availability_index_calc.py
python code/availability_index_robustness.py
python -m unittest code/test_availability_index_robustness.py
```

The first command independently reproduces the baseline through minute-level,
event-boundary, and cohort-deficit calculations. The second writes the baseline and
sensitivity tables to `results/`. The third checks fixed numerical results, exact-count
handling, interval bounds, censoring, and equality of the two WSDH integrals.

## Repository contents

```text
service-availability-europe-west2/
|-- README.md
|-- LICENSE
|-- data/
|   `-- service_cohorts.csv
|-- code/
|   |-- availability_index_calc.py
|   |-- availability_index_robustness.py
|   `-- test_availability_index_robustness.py
|-- results/
|   |-- main_metrics.csv
|   |-- threshold_sensitivity.csv
|   |-- leave_one_out.csv
|   |-- filestore_sensitivity.csv
|   `-- cohort_contributions.csv
`-- docs/
    |-- source_audit.md
    |-- cleaned_dataset.md
    |-- calculation_spec.md
    |-- piecewise_results.md
    |-- summary_metrics.md
    |-- verification.md
    `-- robustness_analysis.md
```

## Inputs and rules

The six baseline cohorts are Cloud Storage ReadObject, unreplicated Bigtable, Cloud
Tasks, Cloud Scheduler, Google Kubernetes Engine nodes, and reachable Virtual Private
Cloud virtual machines. The available fraction for each cohort is set to the reported
value during its impact window and to 1 outside that window. The VPC fraction uses the
exact count ratio, 2,234/3,509.

Records without a reported numerical availability fraction are excluded rather than
imputed. Filestore is excluded from the baseline because
the report's timestamps imply 905 minutes while its text states 630 minutes; both
readings are evaluated only as sensitivity cases.

For cohort `i` and minute `t`, `f_i(t)` is its normalized available fraction. With
equal weights, the aggregate index is

```text
availability_index(t) = sum_i w_i f_i(t) / sum_i w_i
WSDH = sum_t [1 - availability_index(t)] delta_t
```

Here `delta_t = 1/60 h`. The aggregate and each cohort fraction remain in `[0,1]`.

## Sensitivity summary

| Case | Minimum index | Time below threshold | Final within-window recovery | WSDH |
|---|---:|---:|---:|---:|
| Baseline, threshold 0.80 | 0.7077747696 | 720 min | 865 min | 4.1213276812 h |
| Threshold 0.70 | 0.7077747696 | 0 min | 0 min | 4.1213276812 h |
| Threshold 0.90 | 0.7077747696 | 1,155 min | Not observed within window | 4.1213276812 h |
| Omit BT | 0.7893297236 | 198 min | 379 min | 2.2505932174 h |
| Omit GKE | 0.7633297236 | 626 min | 807 min | 3.5775932174 h |
| Filestore, 905 min | 0.6852355168 | 685 min | 865 min | 4.5022094410 h |
| Filestore, 630 min | 0.6852355168 | 630 min | 810 min | 4.2075665839 h |

The 0.90 case is right-censored: the index remains below 0.90 at the final observed
minute, so 1,155 minutes is the observation-window length, not a recovery time.

Final within-window recovery means remaining at or above threshold through the end of the observed
window. It is a retrospective convention, not a test of a predeclared recovery-hold
duration. Zero means the threshold was met throughout, not that an outage occurred
and was repaired instantaneously.

## Interpretation limits

- The calculation demonstrates a reproducible accounting procedure.
- Availability is the only evaluated service condition; no customer demand, latency,
  deadline, checkpoint, or backlog-completion series is available.
- The cohorts mix requests, projects, instances, nodes, and virtual machines, so the
  aggregate is a normalized index rather than a physical output quantity.
- Equal weights are transparent illustrative weights, not business or policy weights.
- Threshold sensitivity does not validate any threshold.
- Leave-one-out analysis describes selection sensitivity, not service importance.
- The public incident report provides no paired electrical or cooling profile.
- The outputs do not support provider comparisons or planning resilience credit.

Source percentages described as approximate remain approximate. Ten-decimal output
supports arithmetic comparison, not a claim of corresponding measurement precision.

## Data source

The primary source is the official Google Cloud incident report, *Multiple Cloud
products experiencing elevated error rates, latencies or service unavailability in
europe-west2*, incident `fmEL9i2fArADKawkZAa2`, posted 29 July 2022:

https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2

Every numerical input is traced in `docs/source_audit.md`. Missing fractions and
conflicting durations are not silently imputed or resolved.

## License

Released under the MIT License. See `LICENSE`.

## Contextual evidence and output naming

Vertex AI online prediction is documented separately in `docs/source_audit.md` as
contextual evidence. It has no reported numerical available fraction and is not added
to the calculation CSV. The baseline remains six cohorts, with Filestore retained only
for sensitivity analysis.

`final_recovery_minutes` is the retrospective within-window result, not the formal
framework's recovery measure based on a predeclared continuous period. A blank value
with `recovery_observed=false` and `right_censored=true` means recovery is not observed
within the window. Zero denotes passing throughout the window.
