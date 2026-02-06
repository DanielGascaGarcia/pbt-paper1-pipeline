#Code: 9.Boxplot.py
#Description: Generating pivot with relative changes.
#Created 10th May 2023
#Author: mbaxdg6


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv
import seaborn as sns
import matplotlib
matplotlib.rcParams.update({'font.size': 18})
import globals
# -----------------------------------------------------------#
#              Configurable variables
# -----------------------------------------------------------#
id=globals.id;
path2=globals.path2;
fileToRead="BGHourRelativeChange"+str(id);
fileToSave="Boxplot"+str(id);

# -----------------------------------------------------------#
# Obtain the last values
# -----------------------------------------------------------#
total = pd.DataFrame(index=range(len(pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("To")+str(1)+".csv").columns)-2));
for i in reversed(range(24)):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+"lastValues"+".csv");
    data.rename(columns = {'Last_values':str(i)+str("-")+str(i+1)}, inplace = True);
    total[str(i)+"-"+str(i+1)]=1*data[str(i)+str("-")+str(i+1)];
# -----------------------------------------------------------#
# Saving in the correct order
# -----------------------------------------------------------#
total1 = pd.DataFrame(index=range(len(pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("To")+str(1)+".csv").columns)-2));
for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+"lastValues"+".csv");
    data.rename(columns = {'Last_values':"["+str(i)+str("-")+str(i+1)+"]"}, inplace = True);
    print(str(i)+str("-")+str(i+1));
    total1["["+str(i)+"-"+str(i+1)+"]"]=data["["+str(i)+str("-")+str(i+1)+"]"];
total1.to_csv(str(path2)+str(fileToSave)+str(0)+str("-")+str(24)+"total"+".csv",index=False);

# -----------------------------------------------------------#
# Plot the dataframe
# -----------------------------------------------------------#
plt.grid();
pd.DataFrame.boxplot(total, vert = False);
# -----------------------------------------------------------#
# Display the plot
# -----------------------------------------------------------#
plt.xlabel("Blood Glucose Relative Change \n (mg/dL) (mmol/L)");
plt.ylabel("Hours");
plt.axvspan(-2*18.0182, 2*18.0182, color="blue", alpha=0.2)
plt.title("Blood Glucose Relative Change Behaviour, ID: "+str(id));
plt.show();


