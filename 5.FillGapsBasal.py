"""
5.FillGapsBasal.py
Step 5 (basal insulin): fill the minutes between basal rate changes and compute
the most frequent basal rate at each minute across days.

Created: 22 March 2022 (as written in the original header)
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    OhioT1DM records basal insulin as rate changes, so BasalLeftJoined<id>.csv
    only has values at the minutes when a rate was set. This script carries
    each rate forward until the next change (forward fill) and adds, for
    every minute, the mode of the basal rate over all days.

Inputs
    globals.id, globals.path2
    <path2>/BasalLeftJoined<id>.csv   (4.MergeBasal.py)

Output
    <path2>/BasalImputed<id>.csv
    Columns: (index), Key, BasalValue0, BasalValue1, ..., ModeBasalValue
    ModeBasalValue is in the same units as the OhioT1DM basal value.

Notes
    - Filling is done down each day column separately. Forward fill carries a
      rate to the end of the day; the minutes before the first rate change of
      a day are then back-filled with that first rate, not with the last rate
      of the previous day.
    - When two or more values are equally frequent, mode()[0] keeps the
      smallest one.
"""

import pandas as pd
import os

import globals
# --- Configurable global variables (set in globals.py) ---
id=globals.id;


path2=globals.path2;
fileToRead="BasalLeftJoined"+str(id)+".csv";
fileToSave="BasalImputed"+str(id)+".csv";

# index_col=0 reads the unnamed index column written by 4.MergeBasal.py.
data= pd.read_csv(str(path2)+fileToRead, index_col=0);
# Empty cells -> NaN, then fill each day column: forward (rate stays until
# the next change), then backward (minutes before the first change).
df=data.replace('',float('NaN')).ffill().bfill();
# Most frequent basal rate at each minute across all days (Key is text and
# is excluded by numeric_only).
df["ModeBasalValue"]=df.mode(axis='columns',numeric_only=True)[0];
df.to_csv(str(path2)+str(fileToSave));

