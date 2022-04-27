import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

zh = pd.read_csv("processed_temperatures_P51-1.csv",index_col=0)
press = pd.read_csv("processed_pressures_P51-1.csv",index_col=0)

df = press.merge(zh, how="outer", on="date")


def cut_df(df):
    def longest_stretch(var):
        a = var.values  # Extract out relevant column from dataframe as array
        m = np.concatenate(( [True], np.isnan(a), [True] ))  # Mask
        ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits
        start,stop = ss[(ss[:,1] - ss[:,0]).argmax()]  # Get max interval, interval limits
        return start, stop-1
    limits = np.array([list(longest_stretch(df["t_stream"])),list(longest_stretch(df["charge_diff"])),list(longest_stretch(df["t4"]))])
    lower = max(limits[:,0])
    upper = min(limits[:,1])
    df_out = df.copy().loc[lower:upper, :]
    df_out.reset_index(inplace=True)
    df_out.drop('index',axis=1,inplace=True)
    return df_out

cut = cut_df(df)

zh_c = cut[["date","t1","t2","t3","t4"]]
press_c = cut[["date","charge_diff","t_stream"]]

zh_c.to_csv("processed_temperatures_P51-1.csv")
press_c.to_csv("processed_pressures_P51-1.csv")