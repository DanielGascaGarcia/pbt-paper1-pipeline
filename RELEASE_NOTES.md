# Release notes — PBT, Paper 1 Pipeline

DOI (this version): assigned on publication.
Concept DOI, always resolving to the latest version: **10.5281/zenodo.17392920**

This release updates the analysis code. All figures and tables in the current
version of the manuscript are produced by this version.

## Changes that affect reported values

- `9.Boxplot.py` takes its row count from the per-hour files it reads, so every
  available day of each participant enters the hourly box plots.
- `4.MealBolusDetection.py` applies the part of a meal window that passes
  midnight to the next calendar day, and processes the last day of each
  participant in full (participants 570, 588 and 591).

## Other changes

- `5.AggregationExercise.py` takes the per-hour median of steps over the day
  columns (activity category of 2 of the 144 participant-hours).
- The basal panel of Figures 2 and 6–11 is labelled in U/h.
- `G.CGMCoverage.py` reports CGM coverage per participant and per day,
  descriptively.

## Reproducibility

The orchestrator clears `processed/` before every run and stops if any step
fails or any participant is missing an output. Two runs from a clean state
give identical results: the eight tables in `results/tables/` are identical
byte for byte. A demo mode runs the pipeline on synthetic data.

## License

See `LICENSE`.
