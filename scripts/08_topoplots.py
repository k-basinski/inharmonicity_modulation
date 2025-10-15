# %%
import mne
import pickle
import numpy as np
import matplotlib.pyplot as plt

# load evoked potentials
f = open("../results/evokeds.p", "rb")
ev = pickle.load(f)
f.close()

# %%
jitters = [f"j{i}" for i in range(8)]
topo_times = [.1, .14, .18, .22, .26, .3, .34]
vlims = (-1.5, 1.5)

fig, axs = plt.subplots(
    nrows=8, ncols=8, figsize=(12, 10), width_ratios=[5, 5, 5, 5,5,5, 5, 0.5]
)
plt.subplots_adjust(top=2, bottom=.2, hspace=1,)
for i, jit in enumerate(jitters):
    axs[i, 1].set_title(f'j{i}', pad=-6)
    mne.viz.plot_evoked_topomap(
        mne.grand_average(ev[jit]["mismatch_1"]),
        times=topo_times,
        vlim=vlims,
        axes=axs[i, :],
        show=False,
    )

# %%
fig, axs = plt.subplots(
    nrows=7, ncols=8, figsize=(12, 10), width_ratios=[5, 5, 5, 5,5,5, 5, 0.5]
)
plt.subplots_adjust(top=2, bottom=.2, hspace=1,)
for i, jit in enumerate(jitters[1:]):
    axs[i, 1].set_title(f'j{i}', pad=-6)
    mne.viz.plot_evoked_topomap(
        mne.grand_average(ev[jit]["orn_standards"]),
        times=topo_times,
        vlim=vlims,
        axes=axs[i, :],
        show=False,
    )
# %%
