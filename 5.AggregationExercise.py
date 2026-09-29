"""
5.AggregationExercise.py   (header of the original file reads "6.FillGapsExercise.py")
Step 5 (activity data): hourly step counts, median over days and an activity
level flag for every minute of the day.

Created: 5 July 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    1. Sums the wristband steps of each day into 24 hourly totals.
    2. Spreads each hourly total over the 60 minutes of that hour on the
       1,440-minute grid.
    3. For every minute, computes the median over days (Q50ExerciseValue).
    4. Splits the day by the quartiles of that median: FlagE = 1 (below Q1,
       low activity), 3 (at or above Q3, high activity) or 2 (in between).

Inputs
    globals.id, globals.path2
    <path2>/ExerciseLeftJoined<id>.csv   (4.MergeExercise.py; wristband steps)
    <path2>/Pivot_E_wCN.csv              (3.PivotGeneratorExercise.py)

Output
    <path2>/ExerciseImputed<id>.csv
    Columns: Key (HH:MM:SS, 1,440 rows), Q50ExerciseValue, FlagE.
    The same file name is first used for the intermediate hourly table and is
    then overwritten with this final result.

Notes
    - "Exercise" in the names refers to wristband steps, not to the
      self-reported <exercise> events.
    - An hour with no step readings in a day sums to 0, so it counts as
      "0 steps" rather than as missing data.
    - The mean, median, Q25 and Q75 are computed on the day columns
      (BStepsValue*) only. Earlier versions computed them on all numeric
      columns, so Q50ExerciseValue also included MeanExerciseValue. For the
      six participants of paper 1 this changed FlagE in 2 of 144 hours
      (559 at 09:00 and 575 at 19:00, both high -> medium); the median step
      values themselves can shift slightly in any hour.
      Only Q50ExerciseValue is saved.
    - Because each hourly total is repeated 60 times, the quartiles used for
      the flag are effectively quartiles of 24 hourly values.
"""

import pandas as pd
import numpy as np
import datetime 
import os
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2=globals.path2;
fileToRead="ExerciseLeftJoined"+str(id)+".csv";
fileToSave="ExerciseImputed"+str(id)+".csv";
# Hourly time labels 00:00:00 ... 23:00:00 (24 values), built below.
dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=60);
print(str(path2)+fileToRead); 
secArray=[];
#----------------------------------------------------------------------------------
# Generate aggregation
#----------------------------------------------------------------------------------
data= pd.read_csv(str(path2)+fileToRead);
# Key "HH:MM:SS" -> datetime (pandas adds an arbitrary date) so it can be
# resampled. Each day column is summed per hour; all-NaN hours give 0.
data["Key"]= pd.to_datetime(data["Key"])
result = data.resample('60min', on="Key").sum();
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        dt += step;

# Replace the resampled time index by the 24 hourly labels.
result['Key'] = secArray
result.to_csv(str(path2)+str(fileToSave),index=False);
#----------------------------------------------------------------------------------
# Merge
#----------------------------------------------------------------------------------
# Put the 24 hourly totals back on the 1,440-minute grid: they land on
# HH:00:00 and forward fill copies each total to the other 59 minutes.
data1 = pd.read_csv(str(path2)+"Pivot_E"+"_wCN"+".csv")
data2 = pd.read_csv(str(path2)+str(fileToSave));
data1['Key']=data1['Key'].str.strip();
data2['Key']=data2['Key'].str.strip();
output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
df=output1.replace('',float('NaN')).ffill().bfill();
# Summary across days, per minute, computed on the day columns only.
dayCols=[c for c in df.columns if c.startswith('BStepsValue')];  # day columns only
df["MeanExerciseValue"]=df[dayCols].mean(axis='columns');
df["Q50ExerciseValue"]=df[dayCols].quantile(0.5,axis='columns');
df["Q25ExerciseValue"]=df[dayCols].quantile(0.25,axis='columns');
df["Q75ExerciseValue"]=df[dayCols].quantile(0.75,axis='columns');
#----------------------------------------------------------------------------------
# Statistics of median
#----------------------------------------------------------------------------------
# Quartiles of the per-minute median over the whole day, used for the flag.
q25=df["Q50ExerciseValue"].quantile(0.25);
q50=df["Q50ExerciseValue"].quantile(0.5);
q75=df["Q50ExerciseValue"].quantile(0.75);
max=df["Q50ExerciseValue"].max();
print(q25);
print(q50);
print(q75);
#----------------------------------------------------------------------------------
# Generation of Flag
#----------------------------------------------------------------------------------
values=pd.DataFrame();       
# Number of rows (non-empty values in the first column, Key) = 1,440.
values=df.count(axis=0)[0];
Flag=[];

# FlagE: 1 = below Q1 (low activity), 3 = at or above Q3 (high), 2 = in between.
for i in range(values):
 if df.loc[i, 'Q50ExerciseValue']<q25:
    Flag.append(1);
 elif df.loc[i, 'Q50ExerciseValue']>=q75:
    Flag.append(3);
 else:
    Flag.append(2);
print(Flag);
df["FlagE"]=Flag;
# df["Q50ExerciseValue"]=df["Q50ExerciseValue"].div(max);
#----------------------------------------------------------------------------------
# Generation of Flag
#----------------------------------------------------------------------------------
# Save only the key, the median and the flag (overwrites the hourly table).
df[["Key","Q50ExerciseValue","FlagE"]].to_csv(str(path2)+str(fileToSave),index=False);



