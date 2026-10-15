# Implementation notes — PBT, Paper 1 Pipeline

Technical notes on how the code works, for readers who want more detail than
the README gives. Nothing here is needed to run the pipeline.

## Intermediate files, in `processed/`

| File | Contents |
|---|---|
| `BasalImputed{id}.csv` | imputed programmed basal + modal value |
| `ExerciseImputed{id}.csv` | hourly activity (Q50) + intensity flag (`FlagE`) |
| `BGwNMLeftJoined{id}.csv` | cleaned BG with per-minute `Key` |
| `BGHourRelativeChange{id}0To24medians_wCN.csv` | hourly `MedRelChange` (24 h medians) + reliability `Flag` |
| `BasalSimulated{id}.csv` | `ActiveInsulin` and `BasalInfused` (~5-min resolution) |
| `ComparisonJoined{id}.csv` | final integrated table for figures |

Time key: `Key`, time of day as text `HH:MM:SS` (1-minute grid in most steps,
5 minutes in the basal simulation).

## CGM coverage

CGM coverage is not uniform across days: some days carry fewer than the 288
readings a complete day would hold. No day is excluded on that basis. Hours
with no reading contribute nothing to the median for that hour, and the
three-level reliability measure flags hours supported by few days.

Coverage is computed per day by `G.CGMCoverage.py` as the count of non-null
`BGValue2` entries in each per-day `_wCN ` file, expressed against 288 — the
number of readings a complete day would hold at the 5-minute CGM sampling
interval. `BGValue2` is the column as parsed, before meal-related exclusion, so
the figure measures the sensor record rather than the effect of the algorithm.
Two tables are written to `results/tables/`: `CGMCoverage_byID.csv`, with the
number of days and the mean, median, minimum and maximum daily coverage per
participant together with the number and proportion of days at or above 70%,
and `CGMCoverage_byDay.csv`, with the same figure for every individual day.
Both are descriptive: no reported value depends on them.

## Execution order

Per participant: `0.Parser.py` -> `1.ColumnNamer.py` -> `2.Disaggregator.py` ->
`3.PivotGeneratorBasal.py` -> `3.PivotGeneratorBG.py` ->
`3.PivotGeneratorExercise.py` -> `4.MealBolusDetection.py` -> `4.MergeBasal.py` ->
`4.MergeExercise.py` -> `5.AggregationExercise.py` -> `5.FillGapsBasal.py` ->
`5.MergeBGClean.py` -> `6.SimulationBasalAutomated.py` -> `6.SplitHours.py` ->
`7.InterpolationBGHourly.py` -> `8.RelativeChange.py` -> `9.Boxplot.py` ->
`10.PivotGeneratormedians.py` -> `11.MergeRChBasal.py`

Once, after the per-participant loop: `G.CGMCoverage.py` → `G.GraphResults.py` → `G.Graph3DCleanBG.py` →
`G.Graph3DPeaksRemoved.py` → `G.Graph3DComplete.py` → `S.SimulationAbsortion.py`
→ `G.ComposeFigure3.py`

These are called by the orchestrator with `PATIENT_ID` set to `idG`.
`G.ComposeFigure3.py` runs last because it reads the three panel PNGs written
by the `G.Graph3D*` scripts.

## Running on a clean state

Several steps read the per-day files present in `processed/`, and one renames
columns in place, so the orchestrator clears `processed/` before each run.
**Clear it by hand if you run individual steps.**

Each step reads `globals.py` when it starts. **Do not edit `globals.py` while
a run is in progress**, so that every step of the run uses the same
configuration.

## Implementation details

- **Input handling.** Column names are assigned by the position of each
  element in the XML (`1.ColumnNamer.py`, `2.Disaggregator.py`), following the
  structure of the OhioT1DM files. File names are parsed assuming a
  three-digit participant identifier.
- **Day order.** `5.MergeBGClean.py` lists the per-day files in file-name
  order (the file names start with the weekday), so the day columns of
  `BGwNMLeftJoined{id}.csv` and the "Day number" axis of Figure 3 follow that
  order rather than the calendar. No reported statistic depends on it.
- **Meal exclusion.** The window is a fixed 4 hours from each recorded meal.
  The script also classifies each meal as high, medium or low glycaemic, from
  the time to the peak of the low-pass filtered glucose after the meal. This
  classification is reported in the console and is not used by later steps:
  the same 4-hour window is applied to every meal.
- **Activity levels.** An hour without any recorded steps counts as 0 steps.
  In 559 and 588, seven or more hours have 0 steps, so Q1 is 0 and those hours
  are classified as medium.
- **Environment.** pandas 2.2.2 is required: pandas 3 does not support
  interpolation of a frame with a text column or position-based access by
  integer, both used in the pipeline. Figure rendering can differ slightly
  across systems.
- **Figure annotations.** Panel letters and the A/B/C boxes outside Figure 3
  are added afterwards in an image editor.
