# Personalised Basal Tuner (PBT) — Paper 1 Pipeline

**Manuscript:** *Personalised Basal Tuner (PBT): Retrospective Identification of
Basal Insulin Miscalibration in People with Type 1 Diabetes Mellitus.*
Submitted to *BMC Medical Informatics and Decision Making* — under review.

**Repository:** https://github.com/DanielGascaGarcia/pbt-paper1-pipeline

This code produces every table and data figure of the manuscript. A single
orchestrator runs every step in order.

---

## What it does

The pipeline parses CGM, insulin and activity data, removes meal-related
glucose excursions, computes the hourly relative change of BG over a 24-hour
composite day with a reliability flag, simulates the active insulin of the
programmed basal profile (Rayleigh kernel, peak at 1 h), and combines the three
into the figures reported in the manuscript. Further technical detail is in
[`docs/NOTES.md`](docs/NOTES.md).

---

## Data

- OhioT1DM training files (`{id}-ws-training.xml`) for the six participants
  whose sensor band reports step counts — 559, 563, 570, 575, 588 and 591 —
  placed in `raw/`. The test split is not used.
- The dataset is **not redistributed**; it is available for scientific purposes
  from https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html
- Without the dataset, the pipeline can be run on **synthetic** files in the
  same schema (see *Running*). Their output is not comparable with any
  reported result.

---

## Installation

Python 3.9.12. Dependencies are pinned in `requirements.txt`.

```bash
conda create -n pbt python=3.9.12
conda activate pbt
pip install -r requirements.txt
python --version                 # expect 3.9.12
```

A `venv` with Python 3.9 also works: create it, activate it and run
`pip install -r requirements.txt`.

---

## Running

```bash
python 17.ScriptforTestExperiment1.py
```

The orchestrator clears `processed/`, runs the pipeline for every participant,
checks that every participant produced its outputs, and then runs the
aggregate scripts once. It stops with a non-zero exit status if any step fails.

- **Real data:** `DEMO = False` in `globals.py`, with the XML files in `raw/`.
- **Demo mode:** `DEMO = True`. Synthetic files are generated into
  `sample_data/` and every output goes to `demo_output/`; `raw/` and
  `results/` are never touched.

If you run individual scripts by hand, clear `processed/` first.

---

## Outputs

Figures are written to `results/figures/` and tables to `results/tables/`.

| File | Contents | Use |
|---|---|---|
| `Figure12_data.csv`, `Figure12_key_values.csv` | hours by insulin condition per participant, and the values quoted in the text (off-target %, optimal hours per participant) | reported |
| `SumUMedRelChange_byID.csv`, `SummaryStats_UMedRelChange.csv` | per participant, the daily cumulative absolute relative change, and its mean and SD | reported |
| `MedRelChange_extremes.csv` | range of the hourly medians across participants | reported |
| `CGMCoverage_byID.csv`, `CGMCoverage_byDay.csv`, `CGMCoverage_summary.csv` | sensor coverage per participant and per day | reported (days per participant) and diagnostic |

Every figure that carries a number in the manuscript has a corresponding CSV
here, so the reported values can be checked without re-running the pipeline.

### Figure map

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

## Configuration

`globals.py` holds the paths, the participants, the unit conversion and the
figure switches. The parameters of the method itself (exclusion window,
reliability percentiles, activity quartiles, insulin action curve) are set in
the scripts that use them and are described in those scripts' headers.

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
| `FIG3_ZLIM_MGDL` | z-axis range of Figure 3 (0–400 mg/dL), the value set in the three Figure 3 scripts |
| `path1`-`path4` | input, `processed/`, `results/figures/`, `results/tables/` |

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
├─ docs/NOTES.md                     implementation notes
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

## Reproducibility

Two runs of the full pipeline from a clean state give identical results: the
eight tables in `results/tables/` are identical byte for byte.

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
