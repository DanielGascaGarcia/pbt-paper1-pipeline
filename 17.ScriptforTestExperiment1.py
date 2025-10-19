#Code: 17.ScriptforTestExperiment1.py
#Description: Creating pivot table for merge.
#Created 5th July 2023
#Author: mbaxdg6 

import subprocess
import globals


scripts = [
    "globals.py",
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

for script in scripts:
    try:
        print(f" Current id is: "+ str(globals.id))
        print(f"Running {script}...")
        subprocess.run(["python", script], check=True)
        print(f"{script} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script}: clear{e}")
        break

