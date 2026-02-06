#Code: 6.FillGapsExercise.py
#Description: .
#Created 5th July 2023
#Author: mbaxdg6

import pandas as pd
import numpy as np
import datetime 
import os
import globals
# -----------------------------------------------------------#
# --- Configurable global variable ---
# -----------------------------------------------------------#
id = globals.id;
path2=globals.path2;
fileToRead="ExerciseLeftJoined"+str(id)+".csv";
fileToSave="ExerciseImputed"+str(id)+".csv";
dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=60);
# print(str(path2)+fileToRead); 
secArray=[];
#----------------------------------------------------------------------------------
# Generate aggregation
#----------------------------------------------------------------------------------
data= pd.read_csv(str(path2)+fileToRead);
data["Key"]= pd.to_datetime(data["Key"])
result = data.resample('60T', on="Key").sum();
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        dt += step;

result['Key'] = secArray
result.to_csv(str(path2)+str(fileToSave),index=False);
#----------------------------------------------------------------------------------
# Merge
#----------------------------------------------------------------------------------
data1 = pd.read_csv(str(path2)+"Pivot_E"+"_wCN"+".csv")
data2 = pd.read_csv(str(path2)+str(fileToSave));
data1['Key']=data1['Key'].str.strip();
data2['Key']=data2['Key'].str.strip();
output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
df=output1.replace('',float('NaN')).ffill().bfill();
df["MeanExerciseValue"]=df.mean(axis='columns',numeric_only=True);
df["Q50ExerciseValue"]=df.quantile(0.5,axis='columns',numeric_only=True);
df["Q25ExerciseValue"]=df.quantile(0.25,axis='columns',numeric_only=True);
df["Q75ExerciseValue"]=df.quantile(0.75,axis='columns',numeric_only=True);
#----------------------------------------------------------------------------------
# Statistics of median
#----------------------------------------------------------------------------------
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
values=df.count(axis=0)[0];
Flag=[];

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
df[["Key","Q50ExerciseValue","FlagE"]].to_csv(str(path2)+str(fileToSave),index=False);



