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
of the manuscript. It supersedes the previous release, which produced slightly
different values — see *Changes in this release*.

---

## Features

- Input parsing and column normalisation (OhioT1DM)
- Minute-level pivot tables for robust merges
- Meal-related data exclusion and tagging for BG
- Aggregation and imputation of **basal** and **activity**
- Hourly **relative BG change** and 24-hour **median** profile with reliability flag
- **Active insulin** simulation from basal (Rayleigh-like kernel)
- Final merge for multi-panel figures (ΔBG, basal / active insulin, activity)

The analysis covers the six OhioT1DM participants whose sensor band reports
step counts — 559, 563, 570, 575, 588 and 591 — using the training split of the
dataset. The training split provides between 41 and 46 days per participant
(mean 44, approximately six weeks); the manuscript refers to this as the
45-day retrospective window.

---

## Inputs

- OhioT1DM per-participant XML files — **training split only**
  (`{id}-ws-training.xml`) — placed in `raw/`. The test split is not used at
  any stage.
- Intermediate files produced by the pipeline itself, written to `processed/`
- Configuration in `globals.py`

> **Time key:** `Key` (datetime; 1–5 min resolution depending on step).

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

The OhioT1DM dataset is **not redistributed here**. It is freely available for
scientific purposes from
https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html

Because the dataset cannot be redistributed, the repository ships
`S.GenerateSampleData.py`, which produces **fully synthetic** files in the same
XML schema. This lets anyone verify that the code executes end to end without
access to the real data. See *Demo mode* below.

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

Python 3.9.12 with six pinned dependencies (see `requirements.txt`). This is the
environment in which the values reported in the **current version of the
manuscript** reproduce; it is not a record of the environment used for the
original submission.

Either route below works. They differ in one respect: conda installs Python
3.9.12 for you, whereas `venv` requires it to be present already.

**Option A — conda**

```bash
conda create -n pbt python=3.9.12
conda activate pbt
pip install -r requirements.txt
```

**Option B — venv, no conda required**

Check first that Python 3.9 is available (`python3.9 --version`, or
`py -3.9 --version` on Windows). If it is not, install it from python.org or
your system package manager, or use Option A.

```bash
# Linux / macOS
python3.9 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
py -3.9 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Other Python versions have not been tested and are not guaranteed to reproduce
the reported values.

Before running, confirm the interpreter actually in use:

```bash
python --version                              # expect 3.9.12
python -c "import sys; print(sys.executable)"
```

This check matters: several environments on the original development machine
shared the same display name, and running under the wrong one produced
different output.

Reproducibility was verified by executing the full pipeline three times from a
clean state and comparing the resulting artefacts between runs. Seven artefacts
were compared on each occasion and were identical byte for byte. To repeat the
check, run the pipeline twice, copying the contents of `results/tables/` to a
separate directory after the first run, and compare the two.

---

## Running the pipeline

```bash
python 17.ScriptforTestExperiment1.py
```

The orchestrator loops over the participant IDs in `globals.py`, setting
`PATIENT_ID` for each subprocess, then runs the aggregate scripts once. It
clears `processed/` before starting, and exits with a non-zero status if any
step fails — without running the aggregate scripts, which read all participants
at once and would otherwise produce output from an incomplete set.

### With the real dataset

Leave `DEMO = False` in `globals.py` and place the `{id}-ws-training.xml` files
directly in `raw/`. If any expected file is absent the run stops immediately and
names what is missing, rather than failing several steps later.

### Demo mode

Set `DEMO = True` in `globals.py`. The orchestrator regenerates synthetic files
into `sample_data/` and runs on those. Demo mode never reads or writes `raw/`,
so leaving the flag set by accident cannot overwrite data obtained under the
Data Use Agreement.

Demo mode also redirects every output: intermediates, figures and tables are
written under `demo_output/` instead of `processed/` and `results/`. The tables
under `results/tables/` are tracked in the repository, and this keeps a demo run
from overwriting them with synthetic values.

The synthetic generator can also be run on its own:

```bash
python S.GenerateSampleData.py --out ./sample_data --days 5 --ids 559 588
```

**Demo output is meaningless.** It exists to show that the code runs, not to
approximate any result. With the default five days per participant the figures
are sparse and the last day of each participant is incomplete, because the
midnight-overflow trimming needs the following day to close. That is expected.

### A note on state

Several steps collect their inputs by listing whatever per-day files are present
in `processed/`, rather than regenerating a known list, and one step renames
columns in place. A file left behind by an earlier or partial run is therefore
picked up as if it belonged to the current one. The orchestrator clears
`processed/` for this reason; **clear it by hand if you run individual steps.**

Each step runs as a separate process and imports `globals.py` as it stands on
disk at that moment, while the orchestrator reads it once at startup.
**Do not edit `globals.py` while a run is in progress:** steps that start after
the edit use the new values and the ones already finished do not, which splits
the run across two configurations.

### Per-participant sequence

`0.Parser.py` -> `1.ColumnNamer.py` -> `2.Disaggregator.py` ->
`3.PivotGeneratorBasal.py` -> `3.PivotGeneratorBG.py` ->
`3.PivotGeneratorExercise.py` -> `4.MealBolusDetection.py` -> `4.MergeBasal.py` ->
`4.MergeExercise.py` -> `5.AggregationExercise.py` -> `5.FillGapsBasal.py` ->
`5.MergeBGClean.py` -> `6.SimulationBasalAutomated.py` -> `6.SplitHours.py` ->
`7.InterpolationBGHourly.py` -> `8.RelativeChange.py` -> `9.Boxplot.py` ->
`10.PivotGeneratormedians.py` -> `11.MergeRChBasal.py`

### Aggregate scripts (run once, after the per-participant loop)

`G.CGMCoverage.py` → `G.GraphResults.py` → `G.Graph3DCleanBG.py` →
`G.Graph3DPeaksRemoved.py` → `G.Graph3DComplete.py` → `S.SimulationAbsortion.py`
→ `G.ComposeFigure3.py`

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
| `DEMO` | `False` to use `raw/`; `True` to generate and use synthetic data |
| `DEMO_DAYS` | days per participant generated in demo mode |
| `DEMO_SEED` | base seed for the generator, so demo runs are reproducible |
| `MGDL_TO_MMOL` | unit conversion factor (1/18) |
| `FIGURE_TITLES` | `False` for submission figures; `True` to render titles for local review |
| `FIG3_ZLIM_MGDL` | shared z-axis range for the three panels of Figure 3 |
| `path1`-`path4` | input, `processed/`, `results/figures/`, `results/tables/` |

`path1` resolves to `raw/` or to `sample_data/` depending on `DEMO`; `path2` to
`path4` resolve under `demo_output/` when `DEMO` is True and at the top level
otherwise. All four paths are resolved relative to `globals.py`, so the
repository runs as cloned and an individual script can also be run from any
working directory.

---

## Repository layout

```
pbt-paper1-pipeline/
├─ globals.py                        configuration
├─ 0.Parser.py … 11.*.py             per-participant pipeline
├─ G.*.py                            aggregate scripts
├─ S.*.py                            simulation scripts
├─ S.GenerateSampleData.py           synthetic data generator
├─ 17.ScriptforTestExperiment1.py    orchestrator
├─ requirements.txt
├─ CITATION.cff
├─ LICENSE
├─ raw/                              input data (not distributed)
├─ sample_data/                      synthetic data (regenerated; not versioned)
├─ processed/                        intermediates (cleared on each run)
├─ demo_output/                      all demo-mode output (not versioned)
└─ results/
   ├─ figures/
   └─ tables/
```

`sample_data/`, `processed/`, `demo_output/` and `results/figures/` are created
by the code and are listed in `.gitignore`. `raw/` is the only directory you need to create
yourself, and only when running against the real dataset.

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
| CGM coverage tables | `G.CGMCoverage.py` -> `results/tables/` |

---

## Changes in this release

### Corrections that change reported values

- **Off-by-one in the box plot step.** `9.Boxplot.py` derived its row count from
  the column count of a file with a different number of non-data columns,
  discarding the last day of every participant — about 2% of the data — silently,
  because pandas aligns by index. Corrected. The values reported in the
  manuscript were updated accordingly; the changes are on the order of one
  percentage point and no conclusion is affected.

Every figure and table in the current version of the manuscript was regenerated
from this release.

### Changes to presentation only

The analysis, thresholds, exclusion windows and statistical treatment are
unchanged by everything in this subsection.

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

### Changes to how the pipeline is run

- **Synthetic data generator added**, so the pipeline can be executed without
  the OhioT1DM dataset.
- **The orchestrator clears `processed/`** before every run, instead of relying
  on the reader to do it.
- **Demo mode redirects its output** to `demo_output/`. Previously only the
  input path was redirected, so a demo run overwrote the tracked tables under
  `results/tables/` with synthetic values.
- **The per-participant summary files are checked** after the loop: a run stops
  if any of them is absent or empty, rather than leaving the aggregate scripts
  to average over whatever is present.
- **Missing input files are reported up front** rather than surfacing as an
  unrelated error several steps later.
- **A failed step now stops the run** with a non-zero exit status, and the
  aggregate scripts are not executed on an incomplete set.

---

## Documented limitations

- **Column naming depends on element order in the source XML.** `1.ColumnNamer.py`
  assigns column names by position (index 0 = glucose level, 1 = finger stick,
  2 = basal, and so on). This matches the OhioT1DM file structure but would
  mislabel columns if applied to XML with the variables in a different order —
  silently, with no error until several steps later. The synthetic generator
  emits the elements in the required order for the same reason.
- **Parsing failures are silent.** The parsing and column-naming steps wrap each
  variable in a bare `except` and print a message rather than stopping. A
  variable that fails to parse produces no `_wCN` file and the pipeline
  continues. Check the console output of steps 0 and 1 before trusting a run.
- **Day columns are ordered by the filesystem.** `5.MergeBGClean.py` collects
  per-day files with `os.listdir` without sorting, so the day columns of
  `BGwNMLeftJoined{id}.csv` (`BGValue0`, `BGValue1`, …) are indexed in
  filesystem order rather than by date. No reported statistic depends on that
  order: all summaries are computed per hour of day or per participant. Note
  that a naive `sorted()` would not fix this, because the filenames carry the
  weekday before the date.
- **Panel letters and annotation boxes are added manually.** `G.ComposeFigure3.py`
  assembles and labels the panels of Figure 3. Elsewhere in the manuscript the
  A/B/C markers and the boxes around the intervals they identify are applied
  afterwards in an image editor. The underlying values are unaffected.
- **Exact rendering is not guaranteed across systems.** Font availability and
  backend differences change pixel output. The values are reproducible; the
  rendering is not bit-identical.

---

## Citation

**Manuscript:** Gasca García, D., Thabit, H., Nutter, P.W., and Harper, S.
*Personalised Basal Tuner (PBT): Retrospective Identification of Basal Insulin
Miscalibration in People with Type 1 Diabetes Mellitus.* Under review.

**Software:** Gasca García, D. *Personalised Basal Tuner (PBT) — Paper 1
Pipeline* [software]. Zenodo. doi: **10.5281/zenodo.17392920**

The DOI above is the concept DOI: it always resolves to the most recent
version. See `CITATION.cff`.

```bibtex
@software{gasca_garcia_pbt_paper1,
  author  = {Gasca García, Daniel},
  title   = {Personalised Basal Tuner (PBT) — Paper 1 Pipeline},
  year    = {2026},
  doi     = {10.5281/zenodo.17392920},
  url     = {https://doi.org/10.5281/zenodo.17392920}
}
```

Related deposits, by concept DOI:

- Paper 2 pipeline — 10.5281/zenodo.17393514
- Software compendium — 10.5281/zenodo.17675141

---

## License

See `LICENSE`.
