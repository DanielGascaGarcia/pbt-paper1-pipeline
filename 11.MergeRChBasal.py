#Description: Merge of values.
#Created 10th May 2023
#Author: mbaxdg6


import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 15})
import globals

# --- Configurable global variable ---
id = globals.id;
path2=globals.path2;
fileToRead1="BGHourRelativeChange"+str(id);
fileToRead2="BasalSimulated"+str(id);
fileToRead3="ExerciseImputed"+str(id);
fileToSave="ComparisonJoined"+str(id);
Sampling_time=0.1;

# -----------------------------------------------------------#
# reading two csv files
# -----------------------------------------------------------#

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
output0 = pd.merge(data1,data2,on='Key',how='left');
output1 = pd.merge(output0,data3,on='Key',how='left');
# Saving the result
output2=output1.interpolate(limit=5, limit_direction="forward");
output2=output1.interpolate(limit=5, limit_direction="backward");
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
col =np.where(np.array(T_Reliability)==1,"Red",np.where(np.array(T_Reliability)==2,"Yellow","Green"));
colordf=pd.DataFrame(col,columns=["Color"]);
print(colordf);
#Exercise
col2 =np.where(np.array(T_Elevel)==1,"#FF81C0",np.where(np.array(T_Elevel)==2,"#C20078","#7E1E9C"));
colordf2=pd.DataFrame(col2,columns=["Color2"]);
print(colordf2);


# -----------------------------------------------------------#
#                    Graph in general
# -----------------------------------------------------------#
fig, (ax1,ax2,ax3)= plt.subplots(nrows=3, sharex=True);
plt.suptitle("Blood Glucose Dynamic, ID: "+str(id));
# -----------------------------------------------------------#
#                    Graph Insulin
# -----------------------------------------------------------#
ax1.set_ylabel("Basal Insulin (U)");
ax1.axhline(linewidth=2, color='Black');
ax1.plot(T_Key,T_ActiveInsulin, 'o',label='Simulated Action Profile', color="blue");
ax1.plot(T_Key,T_BasalInfused, 'o--',label='Preprogrammed Basal Infusion Rate',color="Orange");
ax1.grid(which='major', color='#DDDDDD', linewidth=0.8);
ax1.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);
major_ticks = np.arange(0, 24, 5)
minor_ticks = np.arange(0, 24, 1)
ax1.set_xticks(major_ticks)
ax1.set_xticks(minor_ticks, minor=True)
ax1.legend(bbox_to_anchor = (0.786, 1.035), loc='upper left');
# -----------------------------------------------------------#
#              Graph Relative Blood Glucose
# -----------------------------------------------------------#
T_MedRelChange_=[i/18.0182  for i in T_MedRelChange]
ax2.plot(T_Key,T_MedRelChange_, 'o--',color="Black");
ax2.axhline(linewidth=2, color='Black');
ax2.set_ylabel("BG Rel. Change \n (mg/dL) (mmol/L)");
ax2.grid(which='major', color='#DDDDDD', linewidth=0.8);
ax2.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);

x=0;
y=0;
z=0;
for i in range (len(T_Key)):
    if T_Reliability[i]==1:
        if x==0:
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o',label='Low reliabilty of BG', color=col[i]);
            x=x+1;
        else: 
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o', color=col[i]);            
    elif T_Reliability[i]==2:
        if y==0:
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o',label='Medium reliabilty of BG', color=col[i]);
            y=y+1;
        else: 
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o', color=col[i]);
    else:
        if z==0:
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o',label='High reliabilty of BG', color=col[i]);
            z=z+1;
        else: 
            ax2.plot(T_Key[i],T_MedRelChange_[i],'o', color=col[i]);


# -----------------------------------------------------------#
#              Reordering the labels
# -----------------------------------------------------------#

handles, labels = ax2.get_legend_handles_labels();
# specify order
order = [];  

if labels[0]=="Low reliabilty of BG" and len(order)==0:
    order.append(0);
elif labels[1]=="Low reliabilty of BG" and len(order)==0:
    order.append(1);
else:
    order.append(2);


if labels[0]=="Medium reliabilty of BG" and len(order)==1:
    order.append(0);
elif labels[1]=="Medium reliabilty of BG" and len(order)==1:
    order.append(1);
else:
    order.append(2);


if labels[0]=="High reliabilty of BG" and len(order)==2:
    order.append(0);
elif labels[1]=="High reliabilty of BG" and len(order)==2:
    order.append(1);
else:
    order.append(2);


print(order);

ax2.legend([handles[idx] for idx in order],[labels[idx] for idx in order],bbox_to_anchor = (0.875, 1.035), loc='upper left');


# -----------------------------------------------------------#
#              Graph Exercise
# -----------------------------------------------------------#
ax3.set_ylabel("Median (steps)");
ax3.axhline(linewidth=2, color='Black');
ax3.set_xlabel("Time (h)");
ax3.plot(T_Key,T_Q50ExerciseValue, 'o--', color="black");
ax3.grid(which='major', color='#DDDDDD', linewidth=0.8);
ax3.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);
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

        ax3.legend([handles[idx] for idx in order],[labels[idx] for idx in order],bbox_to_anchor = (0.9, 1.035), loc='upper left');
except:
        ax3.legend(bbox_to_anchor = (0.925, 1.035), loc='upper left');

plt.show();



