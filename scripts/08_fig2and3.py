# %%
from importlib import reload
import mne
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import seaborn as sns
import pickle

jitters = [f"j{i}" for i in range(8)]
ch_picks = ["Fz", "F1", "F2", "AF3", "AF4", "AFz", "F3", "F4", "FC1", "FC2", "FCz"]
topo_times = np.arange(0.1, 0.35, 0.05)
titles_labels = ["harmonic"] + [f"jitter {i}" for i in range(1, 8)]
titles = dict(zip(jitters, titles_labels))
cond_labels = {"std": "standard", "dev_1": "deviant", "mismatch_1": "mismatch"}

# %%
# load evoked potentials
f = open("../results/evokeds.p", "rb")
ev = pickle.load(f)
f.close()


# %%
def plot_erps(jitter, conds, ax):
    d = {cond_labels[cond]: ev[jitter][cond] for cond in conds}
    d.keys()

    if jitter == "j0":
        leg = True
    else:
        leg = False

    mne.viz.plot_compare_evokeds(
        d,
        picks=ch_picks,
        combine="mean",
        show_sensors=leg,
        axes=ax,
        # colors=colors,
        show=False,
        legend=leg,
        ylim=dict(eeg=(-3, 3)),
    )
    ax.set_title(titles[jitter])

    if jitter != "j10":
        ax.set_xlabel(None)


def plot_topomaps(jitter, ax):
    vlims = (-1.5, 1.5)
    ga = mne.grand_average(ev[jitter]["mismatch_1"])
    ga.plot_topomap(times=topo_times, axes=ax, time_unit="ms", vlim=vlims, show=False)


fig, axs = plt.subplots(
    nrows=8,
    ncols=7,
    sharex=False,
    figsize=(12, 18),
    gridspec_kw={"width_ratios": [4, 1, 1, 1, 1, 1, 0.1]},
)
for i, jitter in enumerate(jitters):
    plot_erps(jitter, ["std", "dev_1", "mismatch_1"], axs[i, 0])
    plot_topomaps(jitter, axs[i, 1:])

plt.tight_layout()


plt.savefig("../results/figures/fig2.png", dpi=300)
plt.show()
# %%


fig, axs = plt.subplots(nrows=8, ncols=7, figsize=(6, 22))

for i, jitter in enumerate(jitters):
    plot_topomaps(jitter, axs[i, :])

plt.show()


# %%

d = {titles[jit]: ev[jit]["mismatch_1"] for jit in jitters}

mne.viz.plot_compare_evokeds(
    d,
    picks=ch_picks,
    combine="mean",
    show_sensors=True,
    ci=False,
    cmap='viridis',
    title="",
    show=False,
    ylim=dict(eeg=(-1.5, 1.5)),
)
plt.savefig("../results/figures/fig3.png", dpi=300)

# %%
