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

viridis = mpl.colormaps["viridis"]
# %%
# config
participants = list(range(1, 12))
participants = [
    # 1,
    # 2,
    301,
    303,
    309,
    310,
    312,
    314,
    315,
    316,
    317,
    318,
    319,
    320,
    321,
    322,
    323,
    324,
    325,
    326,
    327,
    328,
    329,
    330,
    332,
    333,
    334,
    335,
    336,
    338,
    340,
    341,
    342,
    404,
    406,
    407,
    408,
]

data_dir = "/Users/kbas/sci_data/harmonicity_modulation/"

ch_eog = ["EXG1", "EXG2"]
# ch_ecg = ['EXG3', 'EXG4']
ch_exclude = [f"EXG{i}" for i in range(3, 9)]
ch_picks = ["Fz", "F1", "F2", "AF3", "AF4", "AFz", "F3", "F4", "FC1", "FC2", "FCz"]
jitters = [f"j{i}" for i in range(8)]
conditions = ['std', 'dev_1', 'dev_2', 'dev_3', 'mismatch_1', 'mismatch_2', 'mismatch_3', 'orn_standards', 'orn_deviants']


def calculate_evokeds(epochs):
    evokeds = {}
    for jitter in jitters:
        evokeds[jitter] = {
            "std": epochs[f"{jitter}/std"].average(),
            "dev_1": epochs[f"{jitter}/dev_1"].average(),
            "dev_2": epochs[f"{jitter}/dev_2"].average(),
            "dev_3": epochs[f"{jitter}/dev_3"].average(),
        }
        evokeds[jitter]["mismatch_1"] = mne.combine_evoked(
            [evokeds[jitter]["dev_1"], evokeds[jitter]["std"]], 
            weights=[1, -1]
        )
        evokeds[jitter]["mismatch_2"] = mne.combine_evoked(
            [evokeds[jitter]["dev_2"], evokeds[jitter]["std"]], 
            weights=[1, -1]
        )
        evokeds[jitter]["mismatch_3"] = mne.combine_evoked(
            [evokeds[jitter]["dev_3"], evokeds[jitter]["std"]], 
            weights=[1, -1]
        )

        # calculate ORN for inharmonic conditions
        if jitter != 'j0':
            evokeds[jitter]['orn_standards'] = mne.combine_evoked(
                [evokeds[jitter]['std'], evokeds['j0']['std']], 
                weights=[1, -1]
            )
            evokeds[jitter]['orn_deviants'] = mne.combine_evoked(
                [evokeds[jitter]['dev_1'], evokeds['j0']['dev_1']], 
                weights=[1, -1]
            )


    return evokeds


# %%
# build evoked dict structure
ev = {f"j{i}": {j: [] for j in conditions} for i in range(8)}

# for each participant
for p in participants:
    print(f'\nCalculating evoked potentials for participant {p}...')
    # read epochs
    epochs = uf.read_preprocessed_epochs(p, data_dir + "preprocessed")

    # calculate evoked responses
    evoked = calculate_evokeds(epochs)

    # append to ev dict
    for jit in jitters:
        for cond in conditions:
            # skip ORN for j0
            if jit == 'j0' and (cond == 'orn_standards' or cond == 'orn_deviants'):
                pass
            else:
                ev[jit][cond].append(evoked[jit][cond])

    print('...done.')





# %%
# pickle so we can reuse later
f = open("../results/evokeds.p", "wb")

# dump information to that file
pickle.dump(ev, f)

# close the file
f.close()
# %%