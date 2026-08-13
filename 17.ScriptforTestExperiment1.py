#Code: 17.ScriptforTestExperiment1.py
#Description: Orchestrator for the experiment 1 pipeline. Runs every step in
#             order, once per participant, then the aggregation scripts.
#Author: mbaxdg6

import subprocess
import shutil
import sys
import os
import globals

HERE = os.path.dirname(os.path.abspath(__file__))

scripts = [
    "0.Parser.py",
    "1.ColumnNamer.py",
    "2.Disaggregator.py",
    "3.PivotGeneratorBasal.py",
    "3.PivotGeneratorBG.py",
    "3.PivotGeneratorExercise.py",
    "4.MealBolusDetection.py",
    "4.MergeBasal.py",
    "4.MergeExercise.py",
    "5.AggregationExercise.py",
    "5.FillGapsBasal.py",
    "5.MergeBGClean.py",
    "6.SimulationBasalAutomated.py",
    "6.SplitHours.py",
    "7.InterpolationBGHourly.py",
    "8.RelativeChange.py",
    "9.Boxplot.py",
    "10.PivotGeneratormedians.py",
    "11.MergeRChBasal.py",
]

final_scripts = [
    "G.CGMCoverage.py",
    "G.GraphResults.py",
    "G.Graph3DCleanBG.py",
    "G.Graph3DPeaksRemoved.py",
    "G.Graph3DComplete.py",
    "S.SimulationAbsortion.py",
    "G.ComposeFigure3.py",
]

# -----------------------------------------------------------#
# Demo data
# -----------------------------------------------------------#
# In demo mode the synthetic input files are regenerated from scratch, so a
# run never mixes files from different generator settings. This only ever
# touches sample_data/; globals.path1 points at raw/ when DEMO is False and
# the block below is skipped entirely.
print(f"Interpreter: {sys.executable}\n")

if globals.DEMO:
    print("\n========== DEMO MODE: generating synthetic input data ==========\n")
    print("Results produced from these files are meaningless. Do not compare")
    print("them with anything reported in the manuscript.\n")
    shutil.rmtree(globals.path1, ignore_errors=True)
    subprocess.run(
        [sys.executable, "S.GenerateSampleData.py",
         "--out", globals.path1,
         "--days", str(globals.DEMO_DAYS),
         "--seed", str(globals.DEMO_SEED),
         "--ids", *[str(i) for i in globals.ids]],
        check=True, cwd=HERE,
    )
else:
    # -----------------------------------------------------------#
    # Real dataset: fail early and say what is missing
    # -----------------------------------------------------------#
    # Without this check a missing or misplaced dataset surfaces several
    # steps later as an unrelated error, which is a poor first experience
    # for anyone running the code for the first time.
    missing = [i for i in globals.ids
               if not os.path.isfile(os.path.join(globals.path1,
                                                  f"{i}-ws-training.xml"))]
    if missing:
        print("\n========== INPUT DATA NOT FOUND ==========\n")
        print(f"Expected in: {globals.path1}")
        for i in missing:
            print(f"  missing: {i}-ws-training.xml")
        print("\nThe OhioT1DM dataset is not redistributable and is not")
        print("included here. Request it from its custodians under their Data")
        print("Use Agreement, then place the training files listed above in")
        print("the directory shown. Only the '-ws-training' files are used;")
        print("the test portion is not.")
        print("\nTo verify that the pipeline executes without the real data,")
        print("set DEMO = True in globals.py. That runs on synthetic files in")
        print("the same schema; its outputs are meaningless.\n")
        sys.exit(1)

# -----------------------------------------------------------#
# Clean intermediate directory
# -----------------------------------------------------------#
# Not optional, and not only for demo runs. Several steps collect their
# inputs by listing whatever per-day files are present in path2 rather than
# regenerating a known list, so a file left behind by an earlier or partial
# run is picked up as if it belonged to this one. The number of days
# entering the analysis would then depend on the state of the directory
# instead of on the input data.
print(f"Clearing intermediate directory: {globals.path2}")
shutil.rmtree(globals.path2, ignore_errors=True)
for directory in (globals.path2, globals.path3, globals.path4):
    os.makedirs(directory, exist_ok=True)

# -----------------------------------------------------------#
# Per-participant pipeline
# -----------------------------------------------------------#
failures = []
completed = []

for patient_id in globals.ids:
    print(f"\n========== Running pipeline for ID {patient_id} ==========\n")
    env = os.environ.copy()
    env["PATIENT_ID"] = str(patient_id)

    for script in scripts:
        try:
            print(f"Running {script} for ID {patient_id}...")
            subprocess.run([sys.executable, script], check=True, env=env, cwd=HERE)
            print(f"{script} completed successfully.\n")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running {script} for ID {patient_id}: {e}")
            failures.append((patient_id, script))
            break
    else:
        completed.append(patient_id)

# -----------------------------------------------------------#
# Aggregation
# -----------------------------------------------------------#
# The aggregation scripts read every participant at once, so running them
# after a partial pipeline would produce figures and tables silently based
# on an incomplete set. Stop instead.
if failures:
    print("\n========== RUN FAILED ==========\n")
    for patient_id, script in failures:
        print(f"  ID {patient_id}: {script}")
    print("\nAggregation scripts were not run, because they read all")
    print("participants at once and would have produced output from an")
    print("incomplete set. Fix the errors above and re-run.\n")
    sys.exit(1)

# -----------------------------------------------------------#
# Confirm every participant produced its summary file
# -----------------------------------------------------------#
# A step can lose a participant without raising: an empty read, a silent
# exception, a filter that matches nothing. The pipeline then completes and
# the aggregation scripts average over whatever is present. Check explicitly
# rather than rely on a figure looking wrong.
#
# Size is checked as well as existence: a step that opens its output file
# and then fails leaves a zero-byte CSV behind, which os.path.isfile alone
# would accept as a successful run.
expected = {i: f"Boxplot{i}0-24total.csv" for i in globals.ids}
absent = {}
for i, f in expected.items():
    p = os.path.join(globals.path2, f)
    if not os.path.isfile(p):
        absent[i] = f"{f} (not found)"
    elif os.path.getsize(p) == 0:
        absent[i] = f"{f} (empty)"
if absent:
    print("\n========== OUTPUTS MISSING AFTER PIPELINE ==========\n")
    print(f"Expected in: {globals.path2}")
    for i, f in absent.items():
        print(f"  ID {i}: {f}")
    print(f"\n{len(absent)} of {len(globals.ids)} participants produced no")
    print("usable summary file, and every step reported success. Aggregation")
    print("was not run: it reads all participants at once and would have")
    print("produced output from an incomplete set.\n")
    sys.exit(1)
print(f"\nAll {len(globals.ids)} participants produced a summary file.")

for script in final_scripts:
    print(f"\n========== Running {script} (all IDs) ==========\n")
    env_final = os.environ.copy()
    env_final["PATIENT_ID"] = str(globals.idG)
    try:
        subprocess.run([sys.executable, script], check=True, env=env_final, cwd=HERE)
        print(f"{script} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script}: {e}")
        failures.append((globals.idG, script))

if failures:
    print("\n========== RUN FAILED (aggregation) ==========\n")
    for patient_id, script in failures:
        print(f"  {script}")
    sys.exit(1)

print("\n========== RUN COMPLETED ==========\n")
print(f"  IDs attempted : {len(globals.ids)}")
print(f"  IDs completed : {len(completed)}")
if globals.DEMO:
    print("\nThis was a demo run on synthetic data. The outputs are not")
    print("comparable with the reported results.\n")