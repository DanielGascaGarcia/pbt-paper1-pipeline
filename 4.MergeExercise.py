#Code: 4.PreprocessingExercise.py
#Description: Creating  Exercise files to be merged.
#Created 5th July 2023
#Author: mbaxdg6

import pandas as pd
import datetime 
import os
import globals

# -----------------------------------------------------------#
# --- Configurable global variable ---
# -----------------------------------------------------------#
id = globals.id;
path2=globals.path2;
fileToRead=str(id)+"-ws-training";
fileToSave="ExerciseLeftJoined"+str(id)+".csv";

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

# -----------------------------------------------------------#
# Files to read
# -----------------------------------------------------------#

filesExercise=[];
for file in os.listdir(path2):
    if file.startswith(listVariables[16]+str(fileToRead)+str(' ')):
        # print(file); 
        filesExercise.append(file);
print(filesExercise);

# -----------------------------------------------------------#
# Left join
# -----------------------------------------------------------#

if len(filesExercise)>=2:
    # reading two csv files
    data1 = pd.read_csv(str(path2)+"Pivot_E"+"_wCN"+".csv")
    data2 = pd.read_csv(str(path2)+filesExercise[0],usecols = ['Time','BStepsValue']);
    data2.rename(columns = {'BStepsValue':'BStepsValue'+str(0)}, inplace = True);
    data2.rename(columns = {'Time':'Key'}, inplace = True);
    data1['Key']=data1['Key'].str.strip();
    print(data1);
    data2['Key']=data2['Key'].str.strip();
    print(data2);
    # using merge function by setting how='left'
    output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
    for j in range(len(filesExercise)-1):
            data3 = pd.read_csv(str(path2)+filesExercise[j+1],usecols = ['Time','BStepsValue']);
            data3.rename(columns = {'BStepsValue':'BStepsValue'+str(j+1)}, inplace = True);
            data3.rename(columns = {'Time':'Key'}, inplace = True);
            data3['Key']=data3['Key'].str.strip();
            print(data3);
            output1 = pd.merge(output1,data3,suffixes=('',''),on='Key',how='left');
# Saving the result
output1.to_csv(str(path2)+str(fileToSave),index=False);


