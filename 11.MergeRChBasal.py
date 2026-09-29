"""
11.MergeRChBasal.py
Step 11: join the three composite-day results of one participant and draw the
three-panel comparison figure (Figures 6-11, and Figure 2 for 588, of paper 1).

Created: 10 May 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    1. Joins, on the time of day:
         - hourly median BG relative change + reliability flag
           (10.PivotGeneratormedians.py, one row per minute),
         - simulated basal action profile + programmed basal rate
           (6.SimulationBasalAutomated.py, one row every 5 minutes),
         - median steps + activity flag (5.AggregationExercise.py, per minute).
    2. Fills the minutes between the 5-minute basal values by linear
       interpolation and saves the joined table.
    3. Takes one point every 6 minutes and draws three panels:
         top    - simulated action profile (blue) and programmed basal rate (orange)
         middle - median BG relative change, coloured by reliability
                  (red = low, yellow = medium, green = high), with a secondary
                  axis in mmol/L
         bottom - median steps, coloured by activity level
                  (light pink = low, magenta = medium, purple = high)

Inputs
    globals.id, globals.path2, globals.path3, globals.MGDL_TO_MMOL,
    globals.FIGURE_TITLES
    <path2>/BGHourRelativeChange<id>0To24medians_wCN.csv
    <path2>/BasalSimulated<id>.csv
    <path2>/ExerciseImputed<id>.csv

Outputs
    <path2>/ComparisonJoined<id>.csv
    <path3>/Figure6.png ... Figure11.png (559, 563, 570, 575, 588, 591);
    588 also saves Figure2.png. Other IDs save <path3>/<id>.png.

Notes
    - Units of the top panel: with a constant basal rate the simulated action
      profile settles at the same number as the rate (checked: rate 1.0 ->
      action 0.98-1.02), so both curves are in the units of the OhioT1DM
      basal value, a rate per hour, hence the "(U/h)" axis label. (Earlier
      versions labelled it "(U)".)
    - Only the backward interpolation is kept: the forward one on the line
      before is overwritten and has no effect. With limit=5 it fills the 4
      minutes between basal values. It also filled the last 5 minutes of an
      hour with no BG data (588 at 13:00 and 20:00), drawing a stray point
      inside those hours; the BG columns are now restored after it, so
      those hours stay empty. No number changes: G.GraphResults.py reads
      minute 1 of each hour, which was never filled.
    - interpolate() also sees the text column Key; pandas 2.2.2 only warns
      about it (not hidden here), newer pandas raise an error.
    - Legend ordering assumes all three reliability levels are present. If
      one were missing, the index 2 would not exist and the script would stop
      with an IndexError on the BG panel (the activity panel has a try/except
      that falls back to the default legend).
"""


import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 11})
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2=globals.path2;
path3=globals.path3;
os.makedirs(path3, exist_ok=True);
fileToRead1="BGHourRelativeChange"+str(id);
fileToRead2="BasalSimulated"+str(id);
fileToRead3="ExerciseImputed"+str(id);
fileToSave="ComparisonJoined"+str(id);
# Plot one point every 0.1 h = 6 minutes (see the sampling loop below).
Sampling_time=0.1;

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL;

# -----------------------------------------------------------#
# reading two csv files
# -----------------------------------------------------------#

# data1: minute-level median BG relative change and reliability flag;
# data2: 5-minute simulated basal; data3: minute-level median steps and flag.
data1 = pd.read_csv(str(path2)+str(fileToRead1)+str("0To24")+"medians"+"_wCN"+".csv");
data2 = pd.read_csv(str(path2)+str(fileToRead2)+".csv");
data3 = pd.read_csv(str(path2)+str(fileToRead3)+".csv");
data1['Key']=data1['Key'].str.strip();
# print(data1);
data2['Key']=data2['Key'].str.strip();
# print(data2);
data3['Key']=data3['Key'].str.strip();
# print(data2);
# using merge function by setting how='left'
# Left joins on the minute grid of data1 (1,440 rows).
output0 = pd.merge(data1,data2,on='Key',how='left');
output1 = pd.merge(output0,data3,on='Key',how='left');
# Saving the result
# Only the second interpolate() is kept (backward, limit 5 minutes); see header.
output2=output1.interpolate(limit=5, limit_direction="forward");
output2=output1.interpolate(limit=5, limit_direction="backward");
# The interpolation is meant for the 5-minute basal columns. Restore the BG
# columns as they came from step 10, so an hour without BG data stays empty
# instead of getting interpolated points in its last minutes.
output2[["MedRelChange","Flag"]]=output1[["MedRelChange","Flag"]];
output2.to_csv(str(path2)+str(fileToSave)+".csv",index=False);

# -----------------------------------------------------------#
# Conversion to arrays
# -----------------------------------------------------------#
Key=[];
MedRelChange=[];
ActiveInsulin=[];
BasalInfused=[];
Reliability=[];
Q50Exercise=[];

Key=output2["Key"].to_numpy();
MedRelChange=output2["MedRelChange"].to_numpy();
ActiveInsulin=output2["ActiveInsulin"].to_numpy();
BasalInfused=output2["BasalInfused"].to_numpy();
Reliability=output2["Flag"].to_numpy();
Q50ExerciseValue=output2["Q50ExerciseValue"].to_numpy();
Elevel=output2["FlagE"].to_numpy();


T_Key=[];
T_MedRelChange=[];
T_ActiveInsulin=[];
T_BasalInfused=[];
T_Reliability=[];
T_Q50ExerciseValue=[];
T_Elevel=[];
# Sampling
# Keep minutes 1, 7, 13, ... (i % 6 == 1, since True == 1); Key -> hours.
for i in range(len(Key)):
    # print(i);
    (h, m, s) = Key[i].split(':');
    result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
    if i % int(Sampling_time*60) ==True:
        T_Key.append(result);
        T_MedRelChange.append(MedRelChange[i]);
        T_ActiveInsulin.append(ActiveInsulin[i]);
        T_BasalInfused.append(BasalInfused[i]);
        T_Reliability.append(Reliability[i]);
        T_Q50ExerciseValue.append(Q50ExerciseValue[i]);
        T_Elevel.append(Elevel[i]);

# -----------------------------------------------------------#
#                    Generation of levels
# -----------------------------------------------------------#
# Blood Glucose
# Colours: reliability 1 = red (low), 2 = yellow (medium), 3 = green (high).
col =np.where(np.array(T_Reliability)==1,"Red",np.where(np.array(T_Reliability)==2,"Yellow","Green"));
colordf=pd.DataFrame(col,columns=["Color"]);
print(colordf);
#Exercise
# Colours: activity 1 = light pink (low), 2 = magenta (medium), 3 = purple (high).
col2 =np.where(np.array(T_Elevel)==1,"#FF81C0",np.where(np.array(T_Elevel)==2,"#C20078","#7E1E9C"));
colordf2=pd.DataFrame(col2,columns=["Color2"]);
print(colordf2);


# -----------------------------------------------------------#
#                    Graph in general
# -----------------------------------------------------------#
fig, (ax1,ax2,ax3)= plt.subplots(nrows=3, sharex=True, figsize=(12, 9), constrained_layout=True);
if globals.FIGURE_TITLES:
    plt.suptitle("Blood Glucose Dynamic, ID: "+str(id));
# -----------------------------------------------------------#
#                    Graph Insulin
# -----------------------------------------------------------#
# Top panel: both curves are rates per hour (see header note on units).
ax1.set_ylabel("Basal Insulin (U/h)");
ax1.axhline(linewidth=2, color='Black');
ax1.plot(T_Key,T_ActiveInsulin, 'o',label='Simulated Action Profile', color="blue");
ax1.plot(T_Key,T_BasalInfused, 'o--',label='Preprogrammed Basal Infusion Rate',color="Orange");
ax1.grid(which='major', color='#DDDDDD', linewidth=0.8);
ax1.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);
major_ticks = np.arange(0, 24, 5)
minor_ticks = np.arange(0, 24, 1)
ax1.set_xticks(major_ticks)
ax1.set_xticks(minor_ticks, minor=True)
ax1.legend(loc='upper right', fontsize=9, framealpha=0.9);
# -----------------------------------------------------------#
#              Graph Relative Blood Glucose
# -----------------------------------------------------------#
T_MedRelChange_=[i  for i in T_MedRelChange]
ax2.plot(T_Key,T_MedRelChange_, 'o--',color="Black");
ax2.axhline(linewidth=2, color='Black');
ax2.set_ylabel("BG Rel. Change \n (mg/dL)");
ax2.grid(which='major', color='#DDDDDD', linewidth=0.8);
ax2.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);

x=0;
y=0;
z=0;
for i in range (len(T_Key)):
    if T_Reliability[i]==1:
        if x==0:
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o',label='Low reliability of BG', color=col[i]);
            x=x+1;
        else: 
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o', color=col[i]);            
    elif T_Reliability[i]==2:
        if y==0:
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o',label='Medium reliability of BG', color=col[i]);
            y=y+1;
        else: 
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o', color=col[i]);
    else:
        if z==0:
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o',label='High reliability of BG', color=col[i]);
            z=z+1;
        else: 
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o', color=col[i]);


# -----------------------------------------------------------#
#              Reordering the labels
# -----------------------------------------------------------#

# Put the legend entries in the order low, medium, high. Assumes the three
# levels are present (see header).
handles, labels = ax2.get_legend_handles_labels();
# specify order
order = [];  

if labels[0]=="Low reliability of BG" and len(order)==0:
    order.append(0);
elif labels[1]=="Low reliability of BG" and len(order)==0:
    order.append(1);
else:
    order.append(2);


if labels[0]=="Medium reliability of BG" and len(order)==1:
    order.append(0);
elif labels[1]=="Medium reliability of BG" and len(order)==1:
    order.append(1);
else:
    order.append(2);


if labels[0]=="High reliability of BG" and len(order)==2:
    order.append(0);
elif labels[1]=="High reliability of BG" and len(order)==2:
    order.append(1);
else:
    order.append(2);


print(order);

ax2.legend([handles[idx] for idx in order],[labels[idx] for idx in order],loc='upper right', fontsize=9, framealpha=0.9);


# -----------------------------------------------------------#
#              Graph Exercise
# -----------------------------------------------------------#
ax3.set_ylabel("Median (steps)");
ax3.axhline(linewidth=2, color='Black');
ax3.set_xlabel("Time (h)");
ax3.plot(T_Key,T_Q50ExerciseValue, 'o--', color="black");
ax3.grid(which='major', color='#DDDDDD', linewidth=0.8);
ax3.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);
# Same ordering for the activity legend; falls back to the default legend on error.
try:

        # ax3.set_ylim([-2.5, 2.5]);
        x=0;
        y=0;
        z=0;
        for i in range (len(T_Key)):
            if T_Elevel[i]==1:
                if x==0:
                    ax3.plot(T_Key[i],T_Q50ExerciseValue[i],'o',label='Low activity', color=col2[i]);
                    x=x+1;
                else: 
                    ax3.plot(T_Key[i],T_Q50ExerciseValue[i],'o', color=col2[i]);            
            elif  T_Elevel[i]==2:
                if y==0:
                    ax3.plot(T_Key[i],T_Q50ExerciseValue[i],'o',label='Medium activity', color=col2[i]);
                    y=y+1;
                else: 
                    ax3.plot(T_Key[i],T_Q50ExerciseValue[i],'o', color=col2[i]);
            else:
                if z==0:
                    ax3.plot(T_Key[i],T_Q50ExerciseValue[i],'o',label='High activity', color=col2[i]);
                    z=z+1;
                else: 
                    ax3.plot(T_Key[i],T_Q50ExerciseValue[i],'o', color=col2[i]);
        # -----------------------------------------------------------#
        #              Reordering the labels
        # -----------------------------------------------------------#
        handles, labels = ax3.get_legend_handles_labels();
        # specify order
        order = [];  

        if labels[0]=="Low activity" and len(order)==0:
            order.append(0);
        elif labels[1]=="Low activity" and len(order)==0:
            order.append(1);
        else:
            order.append(2);


        if labels[0]=="Medium activity" and len(order)==1:
            order.append(0);
        elif labels[1]=="Medium activity" and len(order)==1:
            order.append(1);
        else:
            order.append(2);


        if labels[0]=="High activity" and len(order)==2:
            order.append(0);
        elif labels[1]=="High activity" and len(order)==2:
            order.append(1);
        else:
            order.append(2);

        ax3.legend([handles[idx] for idx in order],[labels[idx] for idx in order],loc='upper right', fontsize=9, framealpha=0.9);
except:
        ax3.legend(loc='upper right', fontsize=9, framealpha=0.9);

# -----------------------------------------------------------#
#   Secondary axis in mmol/L on the BG panel (ax2 only).
#   Rescale only: the data is drawn once on ax2. Placed here so
#   it inherits the final y limits.
# -----------------------------------------------------------#
# Secondary y axis in mmol/L for the BG panel (same data, rescaled).
ax2b = ax2.twinx();
ax2b.set_ylim([v * MGDL_TO_MMOL for v in ax2.get_ylim()]);
ax2b.set_ylabel("BG Rel. Change \n (mmol/L)");
ax2b.grid(False);

# -----------------------------------------------------------#
#              Save figure
# -----------------------------------------------------------#
# File names used in paper 1; 588 is also Figure 2.
figNames = {559:['Figure6'], 563:['Figure7'], 570:['Figure8'], 575:['Figure9'], 588:['Figure10','Figure2'], 591:['Figure11']};
for name in figNames.get(id, [str(id)]):
    out = path3 + name + '.png';
    plt.savefig(out, dpi=300, bbox_inches='tight');
    print("Saved:", os.path.abspath(out));
plt.show();