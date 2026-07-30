# Personalised Basal Tuner (PBT) — Paper 1 Pipeline

**Manuscript:** *Personalised Basal Tuner (PBT): Retrospective Identification of
Basal Insulin Miscalibration in People with Type 1 Diabetes Mellitus*
Submitted to *BMC Medical Informatics and Decision Making* — under review.

**Repository:** https://github.com/DanielGascaGarcia/pbt-paper1-pipeline

A pipeline to parse and harmonise **CGM / insulin / activity** data, estimate
**hourly relative BG change**, simulate **active insulin** from basal
(Rayleigh-like kernel), and produce the integrated outputs and figures reported
in the manuscript.

This release regenerates every figure and table reported in the current version
of the manuscript.

---

## Features

- Input parsing and column normalisation (OhioT1DM)
- Minute-level pivot tables for robust merges
- Meal-related data exclusion and tagging for BG
- Aggregation and imputation of **basal** and **activity**
- Hourly **relative BG change** and 24-hour **median** profile with reliability flag
- **Active insulin** simulation from basal (Rayleigh-like kernel)
- Final merge for multi-panel figures (ΔBG, basal / active insulin, activity)

The analysis covers the six OhioT1DM participants who reported physical
activity — 559, 563, 570, 575, 588 and 591 — over a 45-day retrospective
window, using the training split of the dataset.

---

## Inputs

- OhioT1DM per-participant XML files — **training split only**
  (`{id}-ws-training.xml`) — placed in `raw/`. The test split is not used at
  any stage.
- Intermediate files produced by the pipeline itself, written to `processed/`
- Configuration in `globals.py`

> **Time key:** `Key` (datetime; 1–5 min resolution depending on step).

The OhioT1DM dataset is **not redistributed here**. It is freely available for
scientific purposes from
https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html

---

## Key outputs

| File | Contents |
|---|---|
| `BasalImputed{id}.csv` | imputed programmed basal + modal value |
| `ExerciseImputed{id}.csv` | hourly activity (Q50) + intensity flag (`FlagE`) |
| `BGwNMLeftJoined{id}.csv` | cleaned BG with per-minute `Key` |
| `BGHourRelativeChange{id}0To24medians_wCN.csv` | hourly `MedRelChange` (24 h medians) + reliability `Flag` |
| `BasalSimulated{id}.csv` | `ActiveInsulin` and `BasalInfused` (~5-min resolution) |
| `ComparisonJoined{id}.csv` | final integrated table for figures |

Every figure that carries a number in the manuscript also has a corresponding
CSV under `results/tables/`, so the reported values can be checked without
re-running the pipeline.

---

## Environment

Python 3.9.12 with six pinned dependencies (see `requirements.txt`).

```bash
conda create -n pbt python=3.9.12
conda activate pbt
pip install -r requirements.txt
```

Before running, confirm the interpreter actually in use:

```bash
python -c "import sys; print(sys.executable)"
```

This check matters: several environments on the original development machine
shared the same display name, and running under the wrong one produced
different output.

---

## Running the pipeline

```bash
python 17.ScriptforTestExperiment1.py
```

The orchestrator loops over the participant IDs in `globals.py`, setting
`PATIENT_ID` for each subprocess, then runs the aggregate scripts once.

**The pipeline is not idempotent.** Some steps do not clear the previous run's
files, and one step renames columns in place, so re-running over a populated
`processed/` folder produces contaminated output. **Clear `processed/` and start
from the parser** for any run intended to reproduce the reported values.

### Per-participant sequence

`0.Parser.py` -> `1.ColumnNamer.py` -> `2.Disaggregator.py` ->
`3.PivotGeneratorBasal.py` -> `3.PivotGeneratorBG.py` ->
`3.PivotGeneratorExercise.py` -> `4.MealBolusDetection.py` -> `4.MergeBasal.py` ->
`4.MergeExercise.py` -> `5.AggregationExercise.py` -> `5.FillGapsBasal.py` ->
`5.MergeBGClean.py` -> `6.SimulationBasalAutomated.py` -> `6.SplitHours.py` ->
`7.InterpolationBGHourly.py` -> `8.RelativeChange.py` -> `9.Boxplot.py` ->
`10.PivotGeneratormedians.py` -> `11.MergeRChBasal.py`

### Aggregate scripts (run once, after the per-participant loop)

`G.GraphResults.py` → `G.Graph3DCleanBG.py` → `G.Graph3DPeaksRemoved.py` →
`G.Graph3DComplete.py` → `S.SimulationAbsortion.py` → `G.ComposeFigure3.py`

These are called by the orchestrator with `PATIENT_ID` set to `idG`.
`G.ComposeFigure3.py` runs last because it reads the three panel PNGs written
by the `G.Graph3D*` scripts.

---

## Configuration

All configuration lives in `globals.py`. Nothing is hardcoded in the individual
scripts.

| Name | Purpose |
|---|---|
| `id` | current participant, read from the `PATIENT_ID` environment variable |
| `ids` | the six participants included in this study |
| `idG` | participant used for the single-subject worked examples (588) |
| `MGDL_TO_MMOL` | unit conversion factor (1/18) |
| `FIGURE_TITLES` | `False` for submission figures; `True` to render titles for local review |
| `FIG3_ZLIM_MGDL` | shared z-axis range for the three panels of Figure 3 |
| `path1`-`path4` | `raw/`, `processed/`, `results/figures/`, `results/tables/` |

---

## Repository layout

```
pbt-paper1-pipeline/
├─ globals.py                        configuration
├─ 0.Parser.py … 11.*.py             per-participant pipeline
├─ G.*.py                            aggregate scripts
├─ S.*.py                            simulation scripts
├─ 17.ScriptforTestExperiment1.py    orchestrator
├─ requirements.txt
├─ CITATION.cff
├─ LICENSE
├─ raw/                              input data (not distributed)
├─ processed/                        intermediates
└─ results/
   ├─ figures/
   └─ tables/
```

---

## Figure map

| Manuscript item | Produced by |
|---|---|
| Figure 2 (= Figure 10, ID 588) | `11.MergeRChBasal.py` |
| Figure 3, panel a — all readings | `G.Graph3DComplete.py` |
| Figure 3, panel b — segments removed | `G.Graph3DPeaksRemoved.py` |
| Figure 3, panel c — remaining readings | `G.Graph3DCleanBG.py` |
| Figure 3, composite | `G.ComposeFigure3.py` |
| Figure 4 | `9.Boxplot.py` (when `id == idG`) |
| Figure 5 | `S.SimulationAbsortion.py` |
| Figures 6–11 | `11.MergeRChBasal.py`, one per participant |
| Figures 12–15 | `G.GraphResults.py` |
| Summary tables | `G.GraphResults.py` -> `results/tables/` |

---

## Changes in this release

**These changes affect how results are presented, not what is computed.** The
analysis, thresholds, exclusion windows and statistical treatment are unchanged.

- **Configuration centralised.** Participant IDs, the unit conversion factor,
  the figure-title switch and the shared axis range moved into `globals.py`.
  One script had a participant ID hardcoded; it produces an illustrative figure
  only and does not feed the results chain.
- **Units reported in both scales.** Summary tables carry both mg/dL and mmol/L
  columns. Figures showing glucose carry both scales natively: secondary axes on
  the box plots, dual-unit tick labels on the heat map colour bar and on the 3D
  panels. The dual scale of one figure was previously assembled by hand and is
  now generated by the code.
- **Figure titles moved to captions**, controlled by `FIGURE_TITLES` instead of
  being edited out by hand after each run.
- **Duplicated computation removed.** One script computed the median and the
  per-participant sums twice and wrote both to the same filenames, the second
  overwriting the first. Both produced identical values.
- **Figure 3 panels made consistent** — identical canvas size, framing and
  z-axis range, composed into a single image by `G.ComposeFigure3.py`.
- **Data behind figures exported** to `results/tables/`.

---

## Documented limitations

- **Column naming depends on element order in the source XML.** `1.ColumnNamer.py`
  assigns column names by position (index 0 = glucose level, 1 = finger stick,
  2 = basal, and so on). This matches the OhioT1DM file structure but would
  mislabel columns if applied to XML with the variables in a different order.
- **Parsing failures are silent.** The parsing and column-naming steps wrap each
  variable in a bare `except` and print a message rather than stopping. A
  variable that fails to parse produces no `_wCN` file and the pipeline
  continues. Check the console output of steps 0 and 1 before trusting a run.
- **Panel letters and annotation boxes are added manually.** The code produces
  the plots; the A/B/C markers and boxes used in the manuscript are applied
  afterwards in an image editor. The underlying values are unaffected.
- **Exact rendering is not guaranteed across systems.** Font availability and
  backend differences change pixel output. The values are reproducible; the
  rendering is not bit-identical.
- **One aggregation step reads files with `os.listdir` without sorting**, so the
  column order of one intermediate table depends on the filesystem. Nothing
  downstream depends on that order.

---

## Citation

**Manuscript:** Gasca García, D., Thabit, H., Nutter, P.W., and Harper, S.
*Personalised Basal Tuner (PBT): Retrospective Identification of Basal Insulin
Miscalibration in People with Type 1 Diabetes Mellitus.* Under review.

**Software:** see `CITATION.cff`. DOI: **[add on release]**

---

## License

See `LICENSE`.
