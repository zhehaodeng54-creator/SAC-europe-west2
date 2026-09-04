# Source audit

| Item | Value |
|---|---|
| Primary data source | Google Cloud Service Health incident report |
| Incident ID | `fmEL9i2fArADKawkZAa2` |
| Page title | `Incident details | Google Cloud Service Health` |
| URL | https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2 |
| Incident title | *Multiple Cloud products experiencing elevated error rates, latencies or service unavailability in europe-west2* |
| Access date | 2 September 2026, with the complete report retrieved through direct HTTP access |
| Report version | Google Cloud Incident Report, posted 29 July 2022; the page history also retains the earlier Mini-IR |
| Overall incident window | 19 July 2022 06:33 to 20 July 2022 21:20, all times US/Pacific |

Every numerical input was transcribed from this single official page. No news report, blog, secondary database, or search-result summary was substituted for the official report.

## Service-level evidence excerpts

Each quoted excerpt contains no more than 25 words.

| cohort_id | Verbatim evidence excerpt | Report location |
|---|---|---|
| CS | "ReadObject availability for buckets located in europe-west2 dropped to approximately 86%" | Incident Report, Regional Impact |
| BT | "~70% of unreplicated Bigtable instances in europe-west2-a experienced 100% data plane unavailability" | Incident Report, Google Cloud Bigtable |
| CT | "6% of projects in europe-west2 ... stopped delivering tasks until 13:24" | Incident Report, Google Cloud Tasks |
| CSch | "6% of projects in europe-west2 ... stopped executing jobs until 13:24" | Incident Report, Google Cloud Scheduler |
| GKE | "57% of regional & zonal cluster nodes in europe-west2-a were fully unavailable" | Incident Report, Google Kubernetes Engine |
| VPC | "all Cloud traffic into and out of 1275 / 3509 VMs in europe-west2-a" | Incident Report, Virtual Private Cloud |
| Filestore | "45% of instances in europe-west2-a experienced service unavailability ... 10:05 ... to ... 01:10 US/Pacific" | Incident Report, Cloud Filestore |

## Approximate source values

The report describes the CS value as "approximately 86%," the BT affected share as "~70%," and the VPC affected share as approximately 35%. These values remain approximate, and no confidence interval is inferred. The VPC entry also reports exact counts of 1,275 affected virtual machines among 3,509. The calculation therefore uses the complete affected-count ratio and its complement, as documented in `cleaned_dataset.md`.

## Contextual evidence excluded from numerical reconstruction

The Google Cloud final incident report, in its Vertex AI online prediction entry,
reports elevated errors from 10:00 to 15:11 PDT on 19 July 2022, a duration of 5 h 11 min.
These times correspond to 17:00 to 22:11 UTC. The entry provides no numerical affected
or available fraction for this service.

This record supports the manuscript's contextual discussion only. It is not included in
`data/service_cohorts.csv`, the six-cohort baseline, or any sensitivity calculation. No
missing fraction is inferred from the reported duration.

Source: [Google Cloud final incident report, 29 July 2022](https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2),
Detailed Description of Impact, Vertex AI online prediction. Contextual entry checked
on 4 September 2026.
