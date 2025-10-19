# Personalised Basal Tuner (PBT) — Paper 1 Pipeline

**Manuscript:** *Towards a Personalised Basal Tuner: Imputing Basal Insulin in People with T1DM*

A streamlined pipeline to parse and harmonise **CGM / insulin / activity** data, estimate **hourly relative BG change**, simulate **active insulin** from basal (Rayleigh-like kernel), and produce integrated outputs for analysis and plotting.

---

## ✨ Features
- Input parsing and column normalisation (e.g., OhioT1DM)
- Minute-level pivot tables for robust merges
- Meal/bolus window detection and tagging for BG
- Aggregation and imputation of **basal** and **activity**
- Hourly **relative BG change** and 24-hour **median** profile with confidence flag
- **Active insulin** simulation from basal (Rayleigh-like kernel)
- Final merge for multi-panel figures (ΔBG, basal/active insulin, activity)

---

## 📥 Inputs (expected)
- Participant/day data (XML/CSV depending on your source)
- Intermediate files produced by the pipeline itself
- Parameters in `globals.py` (e.g., `id`, working paths, base date, timezone)

> **Time key:** `Key` (datetime; 1–5 min resolution depending on step).

---

## 📤 Key Outputs
- `BasalImputed{id}.csv` — imputed programmed basal + modal value
- `ExerciseImputed{id}.csv` — hourly activity (Q50) + intensity flag (`FlagE`)
- `BGwNMLeftJoined{id}.csv` — cleaned BG with per-minute `Key`
- `BGHourRelativeChange{id}0To24medians_wCN.csv` — hourly **MedRelChange** (24h medians) + confidence **Flag**
- `BasalSimulated{id}.csv` — **ActiveInsulin** and **BasalInfused** (~5-min resolution)
- `ComparisonJoined{id}.csv` — final integrated table for figures (ΔBG, IA/basal, activity)
- Figures produced by plotting scripts (boxplot + multi-panel plots)

---

## ▶️ Execution Order
Run the orchestrator `17.ScriptforTestExperiment1.py`. It calls the scripts in this exact sequence:

1. `globals.py`
2. `0.Parser.py`
3. `1.ColumnNamer.py`
4. `2.Disaggregator.py`
5. `3.PivotGeneratorBasal.py`
6. `3.PivotGeneratorBG.py`
7. `3.PivotGeneratorExercise.py`
8. `4.MealBolusDetection.py`
9. `4.MergeBasal.py`
10. `4.MergeExercise.py`
11. `5.AggregationExercise.py`
12. `5.FillGapsBasal.py`
13. `5.MergeBGClean.py`
14. `6.SimulationBasalAutomated.py`
15. `6.SplitHours.py`
16. `7.InterpolationBGHourly.py`
17. `8.RelativeChange.py`
18. `9.Boxplot.py`
19. `10.PivotGeneratormedians.py`
20. `11.MergeRChBasal.py`

---

## ⚙️ Requirements
- **Python** ≥ 3.10
- Packages: `pandas`, `numpy`, `scipy`, `matplotlib` (recommended: `tqdm`)

Install (example):
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 🚀 Quick Start
### A) Full pipeline
```bash
python 17.ScriptforTestExperiment1.py
```

### B) By blocks (minimal example)
```bash
# Basal
python 3.PivotGeneratorBasal.py
python 4.MergeBasal.py
python 5.FillGapsBasal.py
python 6.SimulationBasalAutomated.py

# Glucose (BG)
python 3.PivotGeneratorBG.py
python 5.MergeBGClean.py
python 6.SplitHours.py
python 7.InterpolationBGHourly.py
python 8.RelativeChange.py
python 9.Boxplot.py
python 10.PivotGeneratormedians.py

# Activity and final merge
python 3.PivotGeneratorExercise.py
python 4.MergeExercise.py
python 5.AggregationExercise.py
python 11.MergeRChBasal.py
```

---

## 📂 Suggested Layout
```
paper1-pbt/
├─ globals.py
├─ data/        # raw inputs (e.g., OhioT1DM)
├─ work/        # intermediates
├─ outputs/     # final CSVs / figures
└─ scripts/     # (optional) if you prefer to separate .py files
```

---

## 📚 Citation (examples)
- **Manuscript:** *Towards a Personalised Basal Tuner: Imputing Basal Insulin in People with T1DM* (Paper 1).
- **Software (this repository):** Gasca García, D. *PBT — Paper 1 Pipeline (v1.0.0)*. Zenodo/GitHub. DOI: **[add DOI]**.

---

## 📝 License
MIT or Apache-2.0 (add a `LICENSE` file at the repository root).
