"""
4.MergeExercise.py   (header of the original file reads "4.PreprocessingExercise.py")
Step 4 (activity data): join the daily wristband STEP counts of one participant
onto a common minute-by-minute grid.

Created: 5 July 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Takes every daily basis_steps file (listVariables[16]), keeps its Time and
    BStepsValue columns and left-joins them, one day per column, onto the
    1,440-minute grid from 3.PivotGeneratorExercise.py. Despite the "Exercise"
    in the names, the data used are the wristband steps, not the
    self-reported <exercise> events.

Inputs
    globals.id, globals.path2
    <path2>/Pivot_E_wCN.csv   (3.PivotGeneratorExercise.py)
    <path2>/basis_steps<id>-ws-training <Weekday>-<YYYY-MM-DD> .csv
    (per-day files written by 2.Disaggregator.py)

Output
    <path2>/ExerciseLeftJoined<id>.csv
    Columns: Key (HH:MM:SS, 1,440 rows), BStepsValue0, BStepsValue1, ...
    one column per day file. Minutes without a reading are empty (NaN).
    Saved without the index column.

Notes
    - Day columns are numbered in the order returned by os.listdir, which is
      not guaranteed to be chronological.
    - If fewer than 2 day files are found, output1 is never created and the
      final save fails with a NameError.
"""

import pandas as pd
import datetime 
import os
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2=globals.path2;
fileToRead=str(id)+"-ws-training";
fileToSave="ExerciseLeftJoined"+str(id)+".csv";

# Data type names, in the OhioT1DM order, used to build file names.
listVariables=['glucose_level',
'finger_stick',
'basal',
'temp_basal',
'bolus',
'meal',
'sleep',
'work',
'stressors',
'hypo_event',
'illness',
'exercise',
'basis_heart_rate',
'basis_gsr',
'basis_skin_temperature',
'basis_air_temperature',
'basis_steps',
'basis_sleep'];

# -----------------------------------------------------------#
# Files to read
# -----------------------------------------------------------#

filesExercise=[];
# Collect the daily files. The space after "-ws-training" matches only
# the per-day files, not the whole-period _wCN file.
for file in os.listdir(path2):
    if file.startswith(listVariables[16]+str(fileToRead)+str(' ')):
        print(file); 
        filesExercise.append(file);
print(filesExercise);

# -----------------------------------------------------------#
# Left join
# -----------------------------------------------------------#

if len(filesExercise)>=2:
    # reading two csv files
    # data1: the 1,440-minute grid from Pivot_E_wCN.csv (3.PivotGeneratorExercise.py).
    data1 = pd.read_csv(str(path2)+"Pivot_E"+"_wCN"+".csv")
    # data2: first day file. Its value column becomes BStepsValue0 and
    # Time is renamed Key so it can be joined to the grid.
    data2 = pd.read_csv(str(path2)+filesExercise[0],usecols = ['Time','BStepsValue']);
    data2.rename(columns = {'BStepsValue':'BStepsValue'+str(0)}, inplace = True);
    data2.rename(columns = {'Time':'Key'}, inplace = True);
    # Strip spaces so " HH:MM:SS" matches "HH:MM:SS".
    data1['Key']=data1['Key'].str.strip();
    print(data1);
    data2['Key']=data2['Key'].str.strip();
    print(data2);
    # using merge function by setting how='left'
    # Left join: keeps all 1,440 minutes; minutes with no reading stay NaN.
    output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
    # Remaining days, one column each: BStepsValue1, BStepsValue2, ...
    for j in range(len(filesExercise)-1):
            data3 = pd.read_csv(str(path2)+filesExercise[j+1],usecols = ['Time','BStepsValue']);
            data3.rename(columns = {'BStepsValue':'BStepsValue'+str(j+1)}, inplace = True);
            data3.rename(columns = {'Time':'Key'}, inplace = True);
            data3['Key']=data3['Key'].str.strip();
            print(data3);
            output1 = pd.merge(output1,data3,suffixes=('',''),on='Key',how='left');
# Saving the result
output1.to_csv(str(path2)+str(fileToSave),index=False);


