DOI (this version): assigned on publication.
Concept DOI, always resolving to the latest version: **10.5281/zenodo.17392920**

## Changes since the previous release

This release corrects three defects, two of which change reported values. Every figure and table in the current version of the manuscript was regenerated from it.

### Corrections that change reported values

- **Off-by-one in the box plot step.** `9.Boxplot.py` derived its row count from the column count of a file with a different number of non-data columns, silently discarding the last day of every participant — about 2% of the data. Corrected. On its own, this changed reported values by roughly one percentage point; no conclusion is affected.
- **Midnight overflow of the meal window.** When a meal window passed midnight, `4.MealBolusDetection.py` removed the remainder from the next CGM file in date order, whatever its date, and on the last day of a participant it tried to open a file that does not exist; the error stopped the removal for the rest of that day, so post-meal readings stayed in the data. The remainder is now removed only when the next file is the next calendar day, and the last day is processed completely. This changes three participants (570, 588 and 591). The mean daily cumulative absolute relative change goes from 117.42 (SD 25.08) to 121.83 (SD 27.81) mg/dL, the minimum hourly median from −20.5 to −35.0 mg/dL (588, 21:00), the off-target hours from 90.3% to 91.0%, and the optimal hours per participant from 2.0 to 1.83. No conclusion is affected.

### Correction that changes no reported value

- **Median of daily step totals.** `5.AggregationExercise.py` computed the per-hour median of steps over all numeric columns after adding the mean column, so the mean entered the median as one more day. The median is now taken over the day columns only. This changes the activity category of 2 of the 144 participant-hours (559 at 09:00 and 575 at 19:00, both from high to medium) and the plotted step values slightly. Figures 6, 9 and 15 were regenerated; no number reported in the manuscript changes.

## Changes to presentation only

- The basal panel of Figures 2 and 6–11 is labelled in U/h, and the reliability legend of the same figures is spelled correctly.
- The interpolation that fills the basal curve no longer draws points in the BG columns during hours without BG data. No number changes.

## New output

- `G.CGMCoverage.py` reports per-participant and per-day CGM coverage to `results/tables/`. Coverage is the count of non-null `BGValue2` entries in each per-day file against 288, the readings a complete day holds at the 5-minute sampling interval; `BGValue2` is the column before meal-related exclusion, so the figure measures the sensor record rather than the effect of the algorithm. Descriptive only: no day is excluded on that basis and no reported value depends on it.

## Reproducibility

- The orchestrator now clears `processed/` before every run. Several steps collect their inputs by listing that directory, so files left by an earlier run were previously picked up as if they belonged to the current one.
- Missing input files are reported up front instead of surfacing as an unrelated error several steps later.
- A failed step now stops the run with a non-zero exit status, and the aggregate scripts are not executed on an incomplete participant set.
- The per-participant summary files are checked after the loop. A run stops if any of them is absent or empty, rather than leaving the aggregate scripts to average over whatever is present.
- A script listed in the orchestrator that is no longer part of the repository was removed from the aggregate sequence.
- `G.Graph3DCleanBG.py` (Figure 3c) now uses `globals.idG`, like the scripts of panels 3a and 3b, so the three panels show the same participant also when the script is run on its own. The figure produced by the orchestrator does not change.
- Verified by two independent runs from a clean state with the final code; the eight tables in `results/tables/` were identical byte for byte.

## Running without the dataset

- `S.GenerateSampleData.py` generates fully synthetic files in the OhioT1DM schema, so the pipeline can be executed end to end without access to the real data. Enabled with `DEMO = True` in `globals.py`, which never reads or writes `raw/`. Synthetic output is not comparable with any reported result.
- Demo mode now redirects its output as well as its input. Intermediates, figures and tables are written under `demo_output/` instead of `processed/` and `results/`. Previously only the input path was redirected, so a demo run overwrote the tracked tables under `results/tables/` with synthetic values.

## Corrections to the manuscript metadata

- Table 1: the participant-selection criterion is the sensor band, not participant reporting. Pump model for 552 and age group for 596 corrected against the dataset documentation.
- Algorithm 1: the line that carries the remainder of a meal window to the next day subtracted zero rather than one day (now `T_fin − 24:00:00`), and now states that the remainder is carried only when the next file is the next calendar day.

## Note on the dataset

The pipeline uses the training split of the OhioT1DM dataset only (files named `{id}-ws-training.xml`). The test split is not used at any stage. The dataset itself is not redistributed here; it is freely available for scientific purposes from the dataset holders.
