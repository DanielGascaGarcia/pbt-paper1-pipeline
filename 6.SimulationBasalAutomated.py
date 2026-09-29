"""
6.SimulationBasalAutomated.py   (header of the original file reads "S.SimulationBasal.py")
Step 6 (basal insulin): model the insulin action produced by the typical basal
profile of one participant over 24 h.

Created: 22 March 2022 (as written in the original header)
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    1. Takes the most frequent basal rate at each minute (ModeBasalValue from
       5.FillGapsBasal.py) and turns it into one small dose every 5 minutes:
       dose = rate / 12 (a rate per hour delivered over 5 minutes).
    2. Gives every dose a rapid-acting insulin action curve: a Rayleigh
       density (scale 1 h) over 0-7 h, sampled every 5 min (85 points),
       multiplied by the dose.
    3. Adds up all the curves. The part that runs past midnight is wrapped
       around and added to the start of the day, so the result is a
       repeating 24 h profile (steady state).

Inputs
    globals.id, globals.path2
    <path2>/BasalImputed<id>.csv   (5.FillGapsBasal.py; uses Key and ModeBasalValue)

Output
    <path2>/BasalSimulated<id>.csv
    Columns: Key (HH:MM:SS every 5 min, 288 rows),
             ActiveInsulin (summed action curves: dose x density per hour),
             BasalInfused  (the basal rate used at that 5-min slot, unchanged)

Notes
    - Only the rapid-acting profile is used (InsulinV is always 1). The other
      three profiles (regular, NPH, long-acting) are kept in the code but are
      never selected.
    - Minutes 1, 6, 11, ... are sampled (i % 5 == 1, since True == 1), and the
      dose time is moved back 1 minute to 0, 5, 10, ... minutes.
    - The zero padding before each dose is int(12*t) + 1 slots, so a dose
      given at time t starts acting one 5-min slot after t. Because of
      floating-point rounding in int(12*t), 14 of the 288 doses start one
      slot earlier than the rest (e.g. the doses at 00:35 and 01:00).
    - The wrap-around assumes the tail past midnight is shorter than 24 h,
      which holds for the 7 h rapid-acting curve.
"""



import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import rayleigh
from scipy.stats import lognorm 
import pandas as pd
from datetime import datetime,timedelta
import datetime 
import os
import matplotlib
matplotlib.rcParams.update({'font.size': 12})

# --- Configurable global variables (set in globals.py) ---
import globals
id=globals.id;

# -----------------------------------------------------------#
# Parameters
# -----------------------------------------------------------#

path2=globals.path2;
fileToRead="BasalImputed"+str(id)+".csv";
fileToSave="BasalSimulated"+str(id)+".csv";



# Insulin types. Only 1 (rapid) is used by this script.
InsulinDict = { "Rapid":1,"Regular": 2,"NPH": 3,"Gargline/Determine": 4}    

                                                                                   #Units to show either mmol/L or mg/dL
t_start=[0];                                                                       #Time to start the simulation in hrs.
# Key = minute of the day; ModeBasalValue = most frequent basal rate at that minute.
data= pd.read_csv(str(path2)+fileToRead);
t = data["Key"];
InsulinMode=data["ModeBasalValue"];
# II: dose per 5-min slot; InsulinV: insulin type of each dose (not a time);
# t_insulin: time of each dose in hours. The inline comments on the next two
# lines come from the original file.
II=[];                                                                             #Insulin Infused in Units  [U].
InsulinV=[];                                                                       #Time in hrs to basal.   
t_insulin=[];                                                                      #Time in hrs to basal.         
Sampling_time=5/60;                                                                #Sampling time in hrs
Basal_infused=[];
# -----------------------------------------------------------#
#Generation of input variables
# -----------------------------------------------------------#
# One dose every 5 minutes: dose = rate / 12, insulin type 1 (rapid).
for i in range(len(t)):
    # print(i);
    (h, m, s) = t[i].split(':');
    result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
    if i % int(Sampling_time*60) ==True:
        t_insulin.append(result-1/60);
        InsulinV.append(1);
        II.append(InsulinMode[i]/12);

# Basal rate at the same 5-min slots, kept as it is (for the output).
for i in range(len(t)):
    if i % 5==True:
       Basal_infused.append(InsulinMode[i]);
# -----------------------------------------------------------#
# Insulin part
# -----------------------------------------------------------#
#Maximum array size to fill up with 0s
# -----------------------------------------------------------#
# Longest array needed: start offset of the last dose + length of its curve.
# Curve lengths (5-min samples): rapid 85, regular 109, NPH 193, long-acting 289.
Size= [];
for i in range(len(II)):    
    T_0 = [];
    for j in range(int(12*t_insulin[i])+1):
        T_0.append(0);
    T_BB=np.array(T_0);
    if InsulinV[i]==1:
        Size.append(len(T_BB)+85);
    elif InsulinV[i]==2:   
        Size.append(len(T_BB)+109);
    elif InsulinV[i]==3:
        Size.append(len(T_BB)+193);
    elif InsulinV[i]==4:
        Size.append(len(T_BB)+289);
    else:
        print("Not a valid value for kind of insulin");
    FP=max(Size);
  
# One row per dose, one column per 5-min slot.
I_MAT=np.full((len(II), FP), 0,dtype=float);

# print(I_MAT);

# -----------------------------------------------------------#
# Insulin doses computation 
# -----------------------------------------------------------#
for i in range(len(II)): 
    # Rapid-acting: Rayleigh density, scale 1 h, sampled over 0-7 h (85 points),
    # shifted to the dose time with zeros in front and padded with zeros after.
    if InsulinV[i]==1:   
        T_0 = [];
        for j in range(int(12*t_insulin[i])+1):
            T_0.append(0);
        T_BB=np.array(T_0);
        T_D = np.linspace(0,7,85);
        a, b = 0, 1
        dist=rayleigh(a, b); 
        FFI=dist.pdf(T_D);
        BIE =II[i]*FFI;  
        BIEF=np.concatenate((T_BB,BIE),axis=0);
        T_0 = [];
        for j in range(FP-len(BIEF)):
            T_0.append(0);
        T_OF=np.array(T_0); #Correction.
        BIEFF=np.concatenate((BIEF,T_OF),axis=0);    
    if InsulinV[i]==2:   
        T_0 = [];
        for j in range(int(12*t_insulin[i])+1):
            T_0.append(0);
        T_BB=np.array(T_0);
        T_D = np.linspace(0,9,109);
        a, b = 0, 2.5
        dist=rayleigh(a, b); 
        FFI=dist.pdf(T_D);
        BIE =II[i]*FFI;  
        BIEF=np.concatenate((T_BB,BIE),axis=0);
        T_0 = [];
        for j in range(FP-len(BIEF)):
            T_0.append(0);
        T_OF=np.array(T_0); #Correction.
        BIEFF=np.concatenate((BIEF,T_OF),axis=0);    
    if InsulinV[i]==3:   
        T_0 = [];
        for j in range(int(12*t_insulin[i])+1):
            T_0.append(0);
        T_BB=np.array(T_0);
        T_D = np.linspace(0,16,193);
        a, b = 0, 5
        dist=rayleigh(a, b); 
        FFI=dist.pdf(T_D);
        BIE =II[i]*FFI;  
        BIEF=np.concatenate((T_BB,BIE),axis=0);
        T_0 = [];
        for j in range(FP-len(BIEF)):
            T_0.append(0);
        T_OF=np.array(T_0); #Correction.
        BIEFF=np.concatenate((BIEF,T_OF),axis=0);    
    if InsulinV[i]==4:   
        T_0 = [];
        for j in range(int(12*t_insulin[i])+1):
            T_0.append(0);
        T_BB=np.array(T_0);
        T_D = np.linspace(0,24,289);
        a, b = 0, 6
        dist=rayleigh(a, b); 
        FFI=dist.pdf(T_D);
        BIE =II[i]*FFI;  
        BIEF=np.concatenate((T_BB,BIE),axis=0);
        T_0 = [];
        for j in range(FP-len(BIEF)):
            T_0.append(0);
        T_OF=np.array(T_0); #Correction.
        BIEFF=np.concatenate((BIEF,T_OF),axis=0);    
    I_MAT[i,]=BIEFF;    
# Total insulin action at every 5-min slot (sum over all doses).
I_MATF=I_MAT.sum(axis=0);
# print(I_MATF);

# -----------------------------------------------------------#
# Graph
# -----------------------------------------------------------#
# Time axis; only its length is used below.
T=np.linspace(0,int(5*len(I_MATF)),len(I_MATF))/60;

T_F=[];
IF_F=[];

# for i in range(int(12*t_start[0]),len(T)-1):
for i in range(len(T)-1):
    T_F.append(T[i]);
    IF_F.append(I_MATF[i]);
    
# Make BasalInfused the same length as the action curve.
if len(T_F)-len(Basal_infused)>0:
    for j in range(len(T_F)-len(Basal_infused)):
                Basal_infused.append(0);
else:
    for j in range(len(Basal_infused)-len(T_F)):
                del Basal_infused[-1];


# Wrap-around: the action after the first 288 slots (past midnight) is moved
# to the start of the day, and all arrays are cut to 288 slots (24 h).
IF_F_Offset=[];
for i in range(len(T_F)-288):
    IF_F_Offset.append(IF_F[i+288]);

for i in range(len(T_F)-288):
    del Basal_infused[-1];
    del T_F[-1];
    del IF_F[-1];


if 288-len(IF_F_Offset)>0:
    for j in range(288-len(IF_F_Offset)):
        IF_F_Offset.append(0);
else:
    for j in range(288-len(IF_F_Offset)):
        del IF_F_Offset[-1];


print(len(T_F));
print(len(Basal_infused));
print(len(IF_F));
print(len(IF_F_Offset));
# Steady-state 24 h profile = first day + the part that spilled past midnight.
IF_F = np.add(IF_F, IF_F_Offset);  

# -----------------------------------------------------------#
# Units
# -----------------------------------------------------------#

# plt.ylabel("Insulin (U)");
# plt.xlabel("Time (h)");
# plt.title("Basal Insulin Dynamic");
# plt.plot(T_F,IF_F, 'o',label='Active Insulin', color="blue");
# plt.plot(T_F,Basal_infused, 'o',label='Basal insulin values',color="Brown");
# plt.ylim([0, 3]);
# plt.grid(which='major', color='#DDDDDD', linewidth=0.8);
# plt.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);

# plt.legend();
# # # Show the plot
# plt.show();


# -----------------------------------------------------------#
# Save values
# -----------------------------------------------------------#
# Build the output: one row per 5-min slot (00:00:00 ... 23:55:00).
df = pd.DataFrame();
di = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=5);
secArray=[];
# -----------------------------------------------------------#
# Generate key
# -----------------------------------------------------------#
while di < end:
        secArray.append(str(di.strftime('%H:%M:%S')));
        di += step;
secArray=pd.DataFrame(secArray, columns=['Key']);
df['Key']=secArray;
# -----------------------------------------------------------#
# Save columns
# -----------------------------------------------------------#
IF_F=pd.DataFrame(IF_F, columns=['ActiveInsulin']); 
Basal_infused=pd.DataFrame(Basal_infused, columns=['BasalInfused']); 
df['ActiveInsulin']=IF_F;
df['BasalInfused']=Basal_infused;
df.to_csv(str(path2)+str(fileToSave),index=False);

