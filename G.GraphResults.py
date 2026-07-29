#Code: G.GraphResults.py
#Description: Graph values of Blood Glucose.
#Created 3rd August 2023
#Author: mbaxdg6

import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
from datetime import datetime,timedelta
import datetime 
matplotlib.rcParams.update({'font.size': 12});
import seaborn as sns
import numpy 
import numpy as np
import os
import globals

path2=globals.path2;
path3=globals.path3;
os.makedirs(path3, exist_ok=True);
path4=globals.path4;
os.makedirs(path4, exist_ok=True);

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL;

# -----------------------------------------------------------#
# Figure titles. Journals put the title in the caption, not in
# the image, so this is off for the submitted figures.
# -----------------------------------------------------------#
def figTitle(text):
    if globals.FIGURE_TITLES:
        plt.title(text);

Complete=pd.DataFrame();  
CompleteBP=pd.DataFrame();  


for id in globals.ids:
   fileToRead="ComparisonJoined"+str(id);
   fileToSave="ComparisonSampled"+str(id);



   # -----------------------------------------------------------#
   # Conversion to arrays
   # -----------------------------------------------------------#
   data = pd.read_csv(str(path2)+str(fileToRead)+".csv");
   Key=[];
   MedRelChange=[];
   ActiveInsulin=[];
   BasalInfused=[];
   Reliability=[];
   Q50Exercise=[];

   Key=data["Key"].to_numpy();
   MedRelChange=data["MedRelChange"].to_numpy();
   ActiveInsulin=data["ActiveInsulin"].to_numpy();
   BasalInfused=data["BasalInfused"].to_numpy();
   Reliability=data["Flag"].to_numpy();
   Q50ExerciseValue=data["Q50ExerciseValue"].to_numpy();
   Elevel=data["FlagE"].to_numpy();


   T_MedRelChange=[];
   T_ActiveInsulin=[];
   T_BasalInfused=[];
   T_Reliability=[];
   T_Q50ExerciseValue=[];
   T_Elevel=[];
   Flag_pos=[];
   Flag_R=[];
   ID=[];
   # Sampling
   for i in range(len(Key)):
      # print(i);
      (h, m, s) = Key[i].split(':');
      result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
      if i % int(60) ==True:
         if numpy.isnan(MedRelChange[i])==True:
            T_Reliability.append(np.nan);
         else:
            T_Reliability.append(Reliability[i]);
         T_Elevel.append(Elevel[i]);
         T_MedRelChange.append(18*MedRelChange[i]);
         T_ActiveInsulin.append(ActiveInsulin[i]);
         T_BasalInfused.append(BasalInfused[i]);

         T_Q50ExerciseValue.append(Q50ExerciseValue[i]);
         
         ID.append(id);
         if MedRelChange[i]>0:
            Flag_pos.append("1. Too little insulin");
         elif MedRelChange[i]<0:
            Flag_pos.append("2. Too much insulin");
         elif MedRelChange[i]==0:
            Flag_pos.append("3. Optimal")   
         else:
            Flag_pos.append("4. Missing")  

         if  Reliability[i]==3:
             Flag_R.append("high");
         elif  Reliability[i]==2:
             Flag_R.append("Medium");
         elif  Reliability[i]==1:
            Flag_R.append("Low")   
         else:
            Flag_R.append(np.nan) 



   dt = datetime.datetime(2010, 12, 1);
   end = datetime.datetime(2010, 12, 1, 23, 59, 59);
   step = datetime.timedelta(minutes=1);
   positive_array=[]
   for i in range(len(T_MedRelChange)):
     positive_array.append(abs(T_MedRelChange[i]));
   # -----------------------------------------------------------#
   #                           Sample
   # -----------------------------------------------------------#
   Sample=pd.DataFrame();   
   medTime=[];
   j=0;
   while dt < end: 
         if j%60==0:
               medTime.append(dt.strftime('%H:%M:%S'));
         j=j+1;
         dt += step;
   Sample['ID']=ID;
   Sample['Time']=medTime;
   Sample['MedRelChange']=[i/18 for i in T_MedRelChange];
   Sample['UMedRelChange']=[i/18 for i in positive_array];
   Sample['Flag']=T_Reliability;
   Sample['ActiveInsulin']=T_ActiveInsulin;
   Sample['BasalInfused']=T_BasalInfused;
   Sample['Q50ExerciseValue']=T_Q50ExerciseValue;
   Sample['FlagE']=T_Elevel;
   Sample['Category']=Flag_pos;
   Sample['FlagR']=Flag_R;

   Sample.to_csv(str(path2)+str(fileToSave)+".csv",index=False);

   temp_df1 =  Sample[(Sample['Category'] =='1. Too little insulin') ]
   temp_df2 =  Sample[(Sample['Category'] =='2. Too much insulin') ]

   temp_df=pd.concat([temp_df1, temp_df2], ignore_index=True, axis=0);
   temp_df.to_csv(str(path2)+str(fileToSave)+"Clean.csv",index=False);

   CompleteBP=pd.concat([CompleteBP, temp_df], ignore_index=True, axis=0);
   Complete=pd.concat([Complete, Sample], ignore_index=True, axis=0);

# -----------------------------------------------------------#
# All results
# -----------------------------------------------------------# 
CompleteBP.sort_values(by=['ID'])
CompleteBP.to_csv(str(path2)+"CompleteBP"+".csv",index=False);
Complete.sort_values(by=['ID'])
Complete.to_csv(str(path2)+"Complete"+".csv",index=False);

# -----------------------------------------------------------#
# Statistics (mg/dL and mmol/L)
# -----------------------------------------------------------#
median_umedrelchange = Complete['UMedRelChange'].median();
df_median = pd.DataFrame({
    'MedianUMedRelChange_mgdL':  [median_umedrelchange],
    'MedianUMedRelChange_mmolL': [median_umedrelchange * MGDL_TO_MMOL],
});
df_median.to_csv(f"{path2}MedianUMedRelChange.csv", index=False);

df_sum = Complete.groupby('ID', as_index=False)['UMedRelChange'].sum();
df_sum = df_sum.rename(columns={'UMedRelChange': 'UMedRelChange_mgdL'});
df_sum['UMedRelChange_mmolL'] = df_sum['UMedRelChange_mgdL'] * MGDL_TO_MMOL;
df_sum.to_csv(f"{path2}SumUMedRelChange.csv", index=False);
print(df_sum);

sns.boxplot(y='UMedRelChange_mgdL', data=df_sum, width=0.1, color="Red");

mean_value = df_sum['UMedRelChange_mgdL'].mean();
sd_value   = df_sum['UMedRelChange_mgdL'].std();
print(f"Mean = {mean_value:.2f} mg/dL ({mean_value*MGDL_TO_MMOL:.3f} mmol/L), "
      f"SD = {sd_value:.2f} mg/dL ({sd_value*MGDL_TO_MMOL:.3f} mmol/L)");

# -----------------------------------------------------------#
# Save summary statistics
# -----------------------------------------------------------#
df_sum.to_csv(path4 + "SumUMedRelChange_byID.csv", index=False);

stats = pd.DataFrame({
    'Statistic':           ['Mean', 'SD'],
    'UMedRelChange_mgdL':  [mean_value, sd_value],
    'UMedRelChange_mmolL': [mean_value * MGDL_TO_MMOL, sd_value * MGDL_TO_MMOL],
});
stats.to_csv(path4 + "SummaryStats_UMedRelChange.csv", index=False);
print("Saved:", os.path.abspath(path4 + "SumUMedRelChange_byID.csv"));
print("Saved:", os.path.abspath(path4 + "SummaryStats_UMedRelChange.csv"));
# -----------------------------------------------------------#
# Display boxplot  
# -----------------------------------------------------------#
plt.ylabel("Mean cumulative relative change (mg/dL)");
plt.xlabel("ID");
plt.grid(which='major', color='#DDDDDD', linewidth=0.8);
plt.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);
plt.axhline(linewidth=2, color='Black');
figTitle("Blood glucose relative change distribution in all individuals");
plt.show();

# -----------------------------------------------------------#
# Locate the extreme outliers of the boxplot
# -----------------------------------------------------------#
max_val = CompleteBP['MedRelChange'].max();
min_val = CompleteBP['MedRelChange'].min();
print("Max:", max_val, " Min:", min_val);

pd.DataFrame({
    'Statistic':          ['Max', 'Min'],
    'MedRelChange_mgdL':  [max_val, min_val],
    'MedRelChange_mmolL': [max_val * MGDL_TO_MMOL, min_val * MGDL_TO_MMOL],
}).to_csv(path4 + "MedRelChange_extremes.csv", index=False);
print("SAVED:", os.path.abspath(path4 + "MedRelChange_extremes.csv"));
# -----------------------------------------------------------#
# Box plot of relative changes by kind or insulin problem  -> Figure 13
# -----------------------------------------------------------#
plt.figure(figsize=(12, 8));
sns.boxplot(y ='MedRelChange',
              x ='ID',data=CompleteBP,  hue = CompleteBP['Category'], width=0.4);

# -----------------------------------------------------------#
# Display the  box plots
# -----------------------------------------------------------#
ax13 = plt.gca();
ax13.set_ylabel("Blood glucose relative change (mg/dL)");
plt.xlabel("Category");
plt.grid(which='major', color='#DDDDDD', linewidth=0.8);
plt.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);
plt.axhline(linewidth=2, color='Black');
figTitle("Blood glucose relative change distribution in all individuals");

# Secondary axis in mmol/L. Rescale only: the data is drawn once on ax13.
ax13b = ax13.twinx();
ax13b.set_ylim([v * MGDL_TO_MMOL for v in ax13.get_ylim()]);
ax13b.set_ylabel("Blood glucose relative change (mmol/L)");
ax13b.grid(False);

plt.savefig(path3 + 'Figure13.png', dpi=300, bbox_inches='tight');
print("Saved:", os.path.abspath(path3 + 'Figure13.png'));
plt.show();
# -----------------------------------------------------------#
# Histogram of relative changes by kind or insulin problem  -> Figure 12
# -----------------------------------------------------------#
df_gb = Complete.groupby(["ID","Category"]).size().unstack(level=1)

# -----------------------------------------------------------#
# Values quoted in the Figure 12 caption
# -----------------------------------------------------------#
counts = Complete['Category'].value_counts();
n_participants = Complete['ID'].nunique();
n_total = len(Complete);                    # 24 h x participants

n_low  = counts.get('1. Too little insulin', 0);
n_high = counts.get('2. Too much insulin', 0);
n_opt  = counts.get('3. Optimal', 0);
n_miss = counts.get('4. Missing', 0);

pct_all    = 100 * (n_low + n_high) / n_total;
pct_scored = 100 * (n_low + n_high) / (n_total - n_miss);
opt_hours_per_day = n_opt / n_participants;

caption = pd.DataFrame({
    'Metric': ['Participants', 'Hours (24 x n)',
               'Too little insulin', 'Too much insulin', 'Optimal', 'Missing',
               'Off-target %, all hours', 'Off-target %, excl. missing',
               'Optimal hours per day per participant'],
    'Value': [n_participants, n_total,
              n_low, n_high, n_opt, n_miss,
              round(pct_all, 1), round(pct_scored, 1),
              round(opt_hours_per_day, 2)],
});
caption.to_csv(path4 + "Figure12_key_values.csv", index=False);
print(caption.to_string(index=False));

df_gb.plot(kind = 'bar', figsize=(12, 8))
# -----------------------------------------------------------#
# Display the  bar chart
# -----------------------------------------------------------#
plt.xlabel("ID");
plt.grid(which='major', color='#DDDDDD', linewidth=1);
plt.yticks([0,2,4,6,8,10,12,14,16,18,20,22,24])
plt.ylabel("Count");
figTitle("Histogram of category levels of blood glucose relative changes");
plt.savefig(path3 + 'Figure12.png', dpi=300, bbox_inches='tight');
print("Saved:", os.path.abspath(path3 + 'Figure12.png'));
plt.show();
df_gb = Complete.groupby(["ID","Category"]).size().unstack(level=1)
df_gb.to_csv(path4 + "Figure12_data.csv");
print("Saved:", os.path.abspath(path4 + "Figure12_data.csv"));
# -----------------------------------------------------------#
# Display the heatmap of relative change  -> Figure 14
# -----------------------------------------------------------#
plt.figure(figsize=(12, 8));
pvR = Complete.pivot_table(values='UMedRelChange',index='Time',columns='ID')
ax14 = sns.heatmap(pvR,cmap="plasma",linecolor='Gray',linewidths=0.5);

# Colour bar ticks placed at round mmol/L values, labelled in both units.
cbar = ax14.collections[0].colorbar;
vmin, vmax = ax14.collections[0].get_clim();
step = 0.5;  # mmol/L between ticks
lo = np.ceil(vmin * MGDL_TO_MMOL / step) * step;
mmol_ticks = np.arange(lo, vmax * MGDL_TO_MMOL + 1e-9, step);
cbar.set_ticks([t / MGDL_TO_MMOL for t in mmol_ticks]);
cbar.set_ticklabels([f"{t/MGDL_TO_MMOL:.0f}  ({t:.1f})" for t in mmol_ticks]);
cbar.set_label("Absolute relative change, mg/dL (mmol/L)");

figTitle("Absolute blood glucose relative change compared");
plt.savefig(path3 + 'Figure14.png', dpi=300, bbox_inches='tight');

# -----------------------------------------------------------#
# Display the heatmap of activity  -> Figure 15
# -----------------------------------------------------------#
plt.figure(figsize=(12, 8));
pvR = Complete.pivot_table(values='Q50ExerciseValue',index='Time',columns='ID')
sns.heatmap(pvR,cmap="inferno",linecolor='Gray',linewidths=0.5);
figTitle("Activity levels compared (steps)");
plt.savefig(path3 + 'Figure15.png', dpi=300, bbox_inches='tight');
print("Saved:", os.path.abspath(path3 + 'Figure15.png'));
plt.show();