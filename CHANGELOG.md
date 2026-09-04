# Local revision notes

## Scope

This revision labels the public reconstruction as a normalized service-availability
index. Its six baseline cohorts, reported fractions, impact windows, equal weights,
and WSDH formula are unchanged. The baseline remains 0.7077747696 minimum index,
720 minutes below 0.80, recovery at 865 minutes, and 4.1213276812 weighted deficit hours.

## File and output changes

- Calculation entry point: `code/availability_index_calc.py`.
- Robustness entry point: `code/availability_index_robustness.py`.
- Tests: `code/test_availability_index_robustness.py`.
- Canonical, correctly quoted input: `data/service_cohorts.csv`.
- Result column for the minimum: `minimum_availability_index`.
- Added result columns: `recovery_observed` and `right_censored`.
- The non-numerical Vertex AI record is excluded from the calculation CSV but retained
  in `docs/source_audit.md` as contextual evidence. The source package remains unchanged.
- Documentation now describes the retrospective observation-window convention and
  the availability-only interpretation.
- Original copyright attribution is retained in `LICENSE`.

## Recovery correction

At threshold 0.90, the whole 1,155-minute observation window remains below threshold.
The recovery cell is now blank, with `recovery_observed=false` and
`right_censored=true`. The previous value of 1,155 was the window endpoint, not an
observed final within-window recovery. Other baseline and sensitivity numerical results remain
unchanged.

## Repository update

This is a clean local package, without Git history or Python caches. No remote commit,
push, release, or archive update has been made. When applying it to an existing
repository, remove superseded entry points and duplicate input tables as part of the
same change; do not leave both naming schemes active. Check any external scripts that
read the renamed minimum-index column. Update the archive identifier only after the
new release is actually published.

## Terminology and source synchronization

The recovery field has been renamed from `sustained_recovery_minutes` to
`final_recovery_minutes` in both entry points, the metrics object, result tables,
documentation, and tests. It describes final within-window recovery, not a formal test
of a predeclared continuous recovery period. Downstream readers must use the new field.

The Vertex AI contextual evidence has been restored to the source audit without adding
a numerical cohort. The seven-row numerical input, all baseline and sensitivity values,
and the right-censoring convention are unchanged. No remote repository or DOI was
updated as part of this synchronization.
