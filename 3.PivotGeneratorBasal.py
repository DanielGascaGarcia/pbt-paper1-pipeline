"""
3.PivotGeneratorBasal.py
Step 3 of the pipeline: build a minute-by-minute time grid for the basal insulin data.

Created: 22 March 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Writes the 1,440 minutes of one day (00:00:00 to 23:59:00, one row per
    minute) as a single column named "Key". Later steps use this grid as the
    time axis onto which the per-day files are merged, so every day ends up
    with exactly 1,440 rows.

Inputs
    globals.path2   output folder. No participant data is read, and the result
                    does not depend on globals.id.

Outputs
    <path2>/Pivot.csv       the same times without a header (intermediate)
    <path2>/Pivot_wCN.csv   the grid with the header "Key" (used downstream)

Notes
    - The date 1 December 2010 is arbitrary; only the time part is written.
    - 3.PivotGeneratorBG.py, 3.PivotGeneratorBasal.py and
      3.PivotGeneratorExercise.py produce identical content and differ only in
      the output file name.
"""

import datetime 
import pandas as pd
import globals


# Start and end of the grid. The loop stops before 23:59:59, so the
# last row is 23:59:00 (1,440 rows in total).
dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=1);   # one row per minute
path2 = globals.path2;
secArray=[];

# Create (or empty) the intermediate file.
open(str(path2)+"Pivot"+".csv", 'w').close();

# Build the list of times as "HH:MM:SS" strings.
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        dt += step;

print(len(secArray));

# Write one time per line (no header).
for j in secArray:
        file = open(str(path2)+"Pivot"+".csv", 'a');
        file.write(str(j));
        print(str(j));
        file.write('\n');
        file.close();


# Re-read the file, name the column "Key" and save the final grid.
df = pd.read_csv(str(path2)+"Pivot"+".csv",  header=None);
df.rename(columns={0: 'Key'}, inplace=True);
df.to_csv(str(path2)+"Pivot"+"_wCN"+".csv", index=False); # save to new csv 