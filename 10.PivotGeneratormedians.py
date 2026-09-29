"""
10.PivotGeneratormedians.py   (header of the original file reads "Computation of relative changes")
Step 10 (meal-based branch): hourly median relative change and reliability
flag, spread over a minute-by-minute day.

Created: 19 April 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    1. Median relative change of each hour, over all days with data
       (MedRelChange). This is the value used for the optimal /
       insufficient / excessive insulin categories.
    2. Reliability flag of each hour from the number of days with data in
       that hour (data points), using the 50th and 70th percentiles of those
       24 counts as thresholds:
           Flag = 1  count below P50            (low reliability)
           Flag = 2  count from P50 up to P70   (medium)
           Flag = 3  count at or above P70      (high reliability)
    3. Writes both values for every minute of the day (each hour repeated
       60 times) so they can be drawn with the other minute-level series.

Inputs
    globals.id, globals.path2
    <path2>/Boxplot<id>0-24total.csv   (9.Boxplot.py)

Outputs
    <path2>/BGHourRelativeChange<id>0To24medians.csv       (no header, intermediate)
    <path2>/BGHourRelativeChange<id>0To24medians_wCN.csv
        Columns: Key (HH:MM:SS, 1,440 rows), MedRelChange (mg/dL), Flag

Notes
    - The medians are read from the median lines of a matplotlib box plot
      drawn on the current axes. This gives the same value as the median of
      each column over its non-empty cells. An hour with no data at all gives
      an empty median.
    - values[i] reads the counts by position from a Series whose labels are
      text ("[0-1]", ...). pandas 2.2.2 accepts this with a FutureWarning,
      which the filter below hides; newer pandas versions would treat i as a
      label and fail. requirements.txt pins pandas 2.2.2.
"""

import warnings
import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv
import seaborn as sns
warnings.simplefilter(action='ignore', category=FutureWarning)

import globals
# --- Configurable global variables (set in globals.py) ---
id=globals.id;
path2=globals.path2;
fileToRead="Boxplot"+str(id);
fileToSave="BGHourRelativeChange"+str(id);
# -----------------------------------------------------------#
dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=1);
secArray=[];
medians_a=[];
Flag_a=[];
# -----------------------------------------------------------#
# Open file and obtain medians
# -----------------------------------------------------------#
# Table of hourly relative changes: one column per hour, one row per day.
total=pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("-")+str(24)+"total"+".csv");
# Draw a box plot only to read its median lines: medians[i][0] = median of hour i.
_, bp = pd.DataFrame.boxplot(total, return_type='both');
medians = [median.get_ydata() for median in bp["medians"]];
# -----------------------------------------------------------#
# Obtain statistics of the number of lectures per hour
# -----------------------------------------------------------#
values=pd.DataFrame();       
# Number of days with data in each hour (non-empty cells per column).
values=total.count(axis='rows');
# Reliability thresholds: 50th and 70th percentiles of the 24 counts.
low_b=np.percentile(values, 50);
upper_b=np.percentile(values, 70);
Flag=[]

# Flag per hour: 1 = low, 2 = medium, 3 = high reliability.
for i in range(len(values)):
 if values[i]<low_b:
    Flag.append(1);
 elif values[i]>=upper_b:
    Flag.append(3);
 else:
    Flag.append(2);
print(Flag);

# -----------------------------------------------------------#
# Obtain the pivot and variables needed to graph
# -----------------------------------------------------------#
open(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv", 'w').close();
# Spread the 24 hourly values over 1,440 minutes: i moves to the next hour
# every 60 minutes.
i=0;
j=1;
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        medians_a.append(medians[i][0]);
        Flag_a.append(Flag[i]);
        # print(i);
        dt += step;
        if j%60==0:
              i=i+1;
        j=j+1;
# -----------------------------------------------------------#
# Write Key, median and flag (no header), then add the header below.
for j in range(len(secArray)):
        file = open(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv", 'a');
        file.write(str(secArray[j])+","+str(medians_a[j])+","+str(Flag_a[j]));
        file.write('\n');
        file.close();
# -----------------------------------------------------------#
df = pd.read_csv(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv",  header=None);
df.rename(columns={0: 'Key',1:'MedRelChange',2:'Flag'}, inplace=True);
df.to_csv(str(path2)+str(fileToSave)+str("0To24")+"medians"+"_wCN"+".csv", index=False); # save to new csv 
