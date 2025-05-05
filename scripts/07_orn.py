# %%
from importlib import reload
import mne
import matplotlib.pyplot as plt
import numpy as np
import utility_funs as uf
import pandas as pd
import matplotlib as mpl
import seaborn as sns
import pickle

reload(uf)
jitters = [f"j{i}" for i in range(8)]
ch_picks = ["Fz", "F1", "F2", "AF3", "AF4", "AFz", "F3", "F4", "FC1", "FC2", "FCz"]

# %%
# load evoked potentials
f = open("../results/evokeds.p", "rb")
ev = pickle.load(f)
f.close()

# %%
# calculate grand-average (standard+deviant) P2 peak latency

# TODO
# make this list contain all standards ad deviants for all jitters
all_standards_deviants_list = []
all_standards_deviants_list = ev['j1']['std']

# calculate grand average and visualize
ga_stadards_deviants = mne.grand_average(all_standards_deviants_list)
ga_stadards_deviants.pick(ch_picks).plot()
# %%
# get p2 peak
p2_peak = ga_stadards_deviants.pick(ch_picks).get_peak(tmin=.1, tmax=.25, mode='pos')[1]
p2_peak
# %%
# for each participant, jitter (j1-j7) and orn_standards and orn_deviants, calculate ORN amplitude +- 25 ms around p2 peak
orn_window = (p2_peak-.025, p2_peak+.025)

# these lines do this for 1 data point
orn_crop = ev['j1']['orn_standards'][0].copy().crop(orn_window[0],orn_window[1]).pick(ch_picks)
orn_amplitude = orn_crop.data.mean() * 1e6
# %%
orn_amplitude
# %%

# for pandas:
row = {
    'pid': '3',
    'jitter': 'j1',
    'std_dev': 'std',
    'orn_amp': .07312
}
rows_list = []
orn_df = pd.DataFrame(rows_list)
orn_df.to_csv('../results/orn_amps.csv')

# next up: one-sample t-test