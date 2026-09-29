"""
4.MergeBasal.py
Step 4 (basal insulin): join the daily basal rates of one participant onto a
common minute-by-minute grid.

Created: 22 March 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Takes every daily basal file (listVariables[2]), keeps its Time and
    BasalValue columns and left-joins them, one day per column, onto the
    1,440-minute grid from 3.PivotGeneratorBasal.py.

Inputs
    globals.id, globals.path2
    <path2>/Pivot_wCN.csv   (3.PivotGeneratorBasal.py)
    <path2>/basal<id>-ws-training <Weekday>-<YYYY-MM-DD> .csv
    (per-day files written by 2.Disaggregator.py)

Output
    <path2>/BasalLeftJoined<id>.csv
    Columns: (unnamed index), Key (HH:MM:SS, 1,440 rows), BasalValue0,
    BasalValue1, ... one column per day file. OhioT1DM records basal as rate
    changes, so only the minutes where the rate was set have a value; the
    rest are empty (NaN).
    Saved WITH the pandas index, so the file has an extra first column
    ("Unnamed: 0" when re-read). 4.MergeExercise.py saves without it.

Notes
    - Day columns are numbered in the order returned by os.listdir, which is
      not guaranteed to be chronological.
    - If fewer than 2 day files are found, output1 is never created and the
      final save fails with a NameError.
"""


import pandas as pd
import os
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2=globals.path2;
fileToRead=str(id)+"-ws-training";
fileToSave="BasalLeftJoined"+str(id)+".csv";

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




filesBasal=[];
# Collect the daily files. The space after "-ws-training" matches only
# the per-day files, not the whole-period _wCN file.
for file in os.listdir(path2):
    if file.startswith(listVariables[2]+str(fileToRead)+str(' ')):
        # print(file); 
        filesBasal.append(file);
print(filesBasal);


if len(filesBasal)>=2:
    # reading two csv files
    # data1: the 1,440-minute grid from Pivot_wCN.csv (3.PivotGeneratorBasal.py).
    data1 = pd.read_csv(str(path2)+'Pivot_wCN'+'.csv')
    # data2: first day file. Its value column becomes BasalValue0 and
    # Time is renamed Key so it can be joined to the grid.
    data2 = pd.read_csv(str(path2)+filesBasal[0],usecols = ['Time','BasalValue']);
    data2.rename(columns = {'BasalValue':'BasalValue'+str(0)}, inplace = True);
    data2.rename(columns = {'Time':'Key'}, inplace = True);
    # Strip spaces so " HH:MM:SS" matches "HH:MM:SS".
    data1['Key']=data1['Key'].str.strip();
    print(data1);
    data2['Key']=data2['Key'].str.strip();
    print(data2);
    # using merge function by setting how='left'
    # Left join: keeps all 1,440 minutes; minutes with no reading stay NaN.
    output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
    # Remaining days, one column each: BasalValue1, BasalValue2, ...
    for j in range(len(filesBasal)-1):
            data3 = pd.read_csv(str(path2)+filesBasal[j+1],usecols = ['Time','BasalValue']);
            data3.rename(columns = {'BasalValue':'BasalValue'+str(j+1)}, inplace = True);
            data3.rename(columns = {'Time':'Key'}, inplace = True);
            data3['Key']=data3['Key'].str.strip();

            print(data3);
            output1 = pd.merge(output1,data3,on='Key',how='left');
# Saving the result
output1.to_csv(str(path2)+str(fileToSave));


