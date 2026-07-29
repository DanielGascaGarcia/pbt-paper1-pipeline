#Code: 4.MergeBasal
#Description: Merge of values.
#Created 22nd March 2023
#Author: mbaxdg6


import pandas as pd
import os
import globals

# -----------------------------------------------------------#
#              Configurable variables
# -----------------------------------------------------------#
id = globals.id;
path2=globals.path2;
fileToRead=str(id)+"-ws-training";
fileToSave="BasalLeftJoined"+str(id)+".csv";

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




filesBasal=[];
for file in os.listdir(path2):
    if file.startswith(listVariables[2]+str(fileToRead)+str(' ')):
        # print(file); 
        filesBasal.append(file);
print(filesBasal);


if len(filesBasal)>=2:
    # reading two csv files
    data1 = pd.read_csv(str(path2)+'Pivot_wCN'+'.csv')
    data2 = pd.read_csv(str(path2)+filesBasal[0],usecols = ['Time','BasalValue']);
    data2.rename(columns = {'BasalValue':'BasalValue'+str(0)}, inplace = True);
    data2.rename(columns = {'Time':'Key'}, inplace = True);
    data1['Key']=data1['Key'].str.strip();
    print(data1);
    data2['Key']=data2['Key'].str.strip();
    print(data2);
    # using merge function by setting how='left'
    output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
    for j in range(len(filesBasal)-1):
            data3 = pd.read_csv(str(path2)+filesBasal[j+1],usecols = ['Time','BasalValue']);
            data3.rename(columns = {'BasalValue':'BasalValue'+str(j+1)}, inplace = True);
            data3.rename(columns = {'Time':'Key'}, inplace = True);
            data3['Key']=data3['Key'].str.strip();

            print(data3);
            output1 = pd.merge(output1,data3,on='Key',how='left');
# Saving the result
output1.to_csv(str(path2)+str(fileToSave));


