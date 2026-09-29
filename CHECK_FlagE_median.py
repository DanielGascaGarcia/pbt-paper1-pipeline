"""
CHECK_FlagE_median.py
One-off check (not part of the pipeline): how much does the activity flag FlagE
change if Q50ExerciseValue is the median of the day columns only, instead of
the median of the day columns plus MeanExerciseValue (as in
5.AggregationExercise.py)?

It reads the same input as 5.AggregationExercise.py, reproduces the current
calculation and the corrected one, and compares them hour by hour.
It also checks that the reproduced "current" result matches the
ExerciseImputed<id>.csv already on disk, so we know the replication is exact.
Nothing is written to disk.
"""
import datetime
import pandas as pd
import globals

IDS = [559, 563, 570, 575, 588, 591]      # paper 1 participants
path2 = globals.path2                     # adjust if each ID uses its own folder


def build_minute_table(id_):
    """Steps 1-2 of 5.AggregationExercise.py: hourly sums spread over 1,440 minutes."""
    data = pd.read_csv(f"{path2}ExerciseLeftJoined{id_}.csv")
    data["Key"] = pd.to_datetime(data["Key"])
    result = data.resample("60min", on="Key").sum()
    dt, end = datetime.datetime(2010, 12, 1), datetime.datetime(2010, 12, 1, 23, 59, 59)
    hours = []
    while dt < end:
        hours.append(dt.strftime("%H:%M:%S"))
        dt += datetime.timedelta(minutes=60)
    result["Key"] = hours
    result = result.reset_index(drop=True)   # the original saves and re-reads this table
    grid = pd.read_csv(f"{path2}Pivot_E_wCN.csv")
    grid["Key"] = grid["Key"].str.strip()
    result["Key"] = result["Key"].str.strip()
    return pd.merge(grid, result, on="Key", how="left").ffill().bfill()


def flag(q50):
    q25, q75 = q50.quantile(0.25), q50.quantile(0.75)
    return q50.apply(lambda v: 1 if v < q25 else (3 if v >= q75 else 2))


rows = []
for id_ in IDS:
    df = build_minute_table(id_)
    day_cols = [c for c in df.columns if c.startswith("BStepsValue")]

    # Current behaviour: the mean column exists when the median is taken.
    cur = df.copy()
    cur["MeanExerciseValue"] = cur.mean(axis="columns", numeric_only=True)
    q50_cur = cur.quantile(0.5, axis="columns", numeric_only=True)

    # Corrected: median of the day columns only.
    q50_new = df[day_cols].median(axis="columns")

    f_cur, f_new = flag(q50_cur), flag(q50_new)

    # Sanity check against the file produced by the pipeline.
    saved = pd.read_csv(f"{path2}ExerciseImputed{id_}.csv")
    replica_ok = (saved["FlagE"].values == f_cur.values).all() and \
                 ((saved["Q50ExerciseValue"] - q50_cur).abs() < 1e-9).all()

    # Compare per hour (each hour is 60 identical minutes).
    hourly = pd.DataFrame({"Key": df["Key"], "cur": f_cur, "new": f_new})
    hourly = hourly[hourly["Key"].str.endswith(":00:00")]
    changed = hourly[hourly["cur"] != hourly["new"]]

    rows.append({"id": id_, "days": len(day_cols), "replica_matches_file": replica_ok,
                 "hours_changed": len(changed),
                 "which": ", ".join(f"{k[:5]} {a}->{b}" for k, a, b in
                                    changed[["Key", "cur", "new"]].itertuples(index=False))})

print(pd.DataFrame(rows).to_string(index=False))
