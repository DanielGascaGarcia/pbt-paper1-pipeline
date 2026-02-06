#Code: 6.SimulationBasalAutomated.py
#Description: Simulation of basal values.
#Created 22nd March 2022
#Author: mbaxdg6



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

import globals
id=globals.id;


# -----------------------------------------------------------#
#              Configurable variables
# -----------------------------------------------------------#
path2=globals.path2;
fileToRead="BasalImputed"+str(id)+".csv";
fileToSave="BasalSimulated"+str(id)+".csv";



InsulinDict = { "Rapid":1,"Regular": 2,"NPH": 3,"Gargline/Determine": 4}    

                                                                                   #Units to show either mmol/L or mg/dL
t_start=[0];                                                                       #Time to start the simulation in hrs.
data= pd.read_csv(str(path2)+fileToRead);
t = data["Key"];
InsulinMode=data["ModeBasalValue"];
II=[];                                                                             #Insulin Infused in Units  [U].
InsulinV=[];                                                                       #Time in hrs to basal.   
t_insulin=[];                                                                      #Time in hrs to basal.         
Sampling_time=5/60;                                                                #Sampling time in hrs
Basal_infused=[];
# -----------------------------------------------------------#
#Generation of input variables
# -----------------------------------------------------------#
for i in range(len(t)):
    # print(i);
    (h, m, s) = t[i].split(':');
    result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
    if i % int(Sampling_time*60) ==True:
        t_insulin.append(result-1/60);
        InsulinV.append(1);
        II.append(InsulinMode[i]/12);

for i in range(len(t)):
    if i % 5==True:
       Basal_infused.append(InsulinMode[i]);
# -----------------------------------------------------------#
# Insulin part
# -----------------------------------------------------------#
#Maximum array size to fill up with 0s
# -----------------------------------------------------------#
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
  
I_MAT=np.full((len(II), FP), 0,dtype=float);

# print(I_MAT);

# -----------------------------------------------------------#
# Insulin doses computation 
# -----------------------------------------------------------#
for i in range(len(II)): 
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
I_MATF=I_MAT.sum(axis=0);
# print(I_MATF);

# -----------------------------------------------------------#
# Graph
# -----------------------------------------------------------#
T=np.linspace(0,int(5*len(I_MATF)),len(I_MATF))/60;

T_F=[];
IF_F=[];

# for i in range(int(12*t_start[0]),len(T)-1):
for i in range(len(T)-1):
    T_F.append(T[i]);
    IF_F.append(I_MATF[i]);
    
if len(T_F)-len(Basal_infused)>0:
    for j in range(len(T_F)-len(Basal_infused)):
                Basal_infused.append(0);
else:
    for j in range(len(Basal_infused)-len(T_F)):
                del Basal_infused[-1];


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

