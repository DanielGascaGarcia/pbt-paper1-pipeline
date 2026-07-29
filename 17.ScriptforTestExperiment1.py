import subprocess
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
    "10.PivotGeneratorMedians.py",
    "11.MergeRChBasal.py",
]

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
            break


final_scripts = [
    "G.GraphResults.py",
    "G.Graph3DCleanBG.py",
    "G.Graph3DPeaksRemoved.py",
    "G.Graph3DComplete.py",
    "S.SimulationAbsortion.py",
    "G.ComposeFigure3.py",
]

env_final = os.environ.copy()
env_final["PATIENT_ID"] = str(globals.idG)

for script in final_scripts:
    print(f"\n========== Running {script} (all IDs) ==========\n")
    try:
        subprocess.run([sys.executable, script], check=True, env=env_final, cwd=HERE)
        print(f"{script} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script}: {e}")