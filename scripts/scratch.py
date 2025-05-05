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


# %%
# load evoked potentials
f = open("../results/evokeds.p", "rb")
ev = pickle.load(f)
f.close()


# %%
def plot_erps(jitter, conds, ax):
    d = {cond: ev[jitter][cond] for cond in conds}


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
        ylim=dict(eeg=(-4, 4)),
    )
    ax.set_title(jitter)

    if jitter != "j10":
        ax.set_xlabel(None)


fig, axs = plt.subplots(nrows=8, sharex=False, figsize=(6, 22))
for i, jitter in enumerate(jitters):
    plot_erps(jitter, ['std', 'dev_1', 'mismatch_1'], axs[i])

plt.tight_layout()


plt.savefig("../results/figures/erps.png", dpi=300)
plt.show()


# %%
# plot ORN
def plot_erps_orn(jitter, ax):
    d = {
        'harmonic standard': ev['j0']['std'],
        'inharmonic standard': ev[jitter]['std'],
        'ORN (standards)': ev[jitter]['orn_standards']
    }


    if jitter == "j1":
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
        ylim=dict(eeg=(-4, 4)),
    )
    ax.set_title(jitter)

    if jitter != "j10":
        ax.set_xlabel(None)

fig, axs = plt.subplots(nrows=7, sharex=False, figsize=(6, 18))
for i, jitter in enumerate(jitters[1:]):
    plot_erps_orn(jitter, axs[i])

plt.tight_layout()


plt.savefig("../results/figures/erps.png", dpi=300)
plt.show()



# %%
d = {
    "harmonic": evokeds[feature]["harmonic"]["mmn"],
    "inharmonic": evokeds[feature]["inharmonic"]["mmn"],
    "changing": evokeds[feature]["changing"]["mmn"],
    # "inh_deviants": pitch["inh_deviants"]["mmn"],
}
leg = True
mne.viz.plot_compare_evokeds(
    d,
    picks=ch_picks,
    combine="mean",
    show_sensors=leg,
    # axes=ax,
    show=True,
    cmap="viridis",
    legend=leg,
    ylim=dict(eeg=(-4, 4)),
)
# %%
ga = mne.grand_average(evokeds["pitch"]["harmonic"]["mmn"])
times = np.arange(0.05, 0.35, 0.05)
ga.plot_topomap(times)


# %%
def participant_peaks(evoked, mean_window=(-0.025, 0.025), plot=False, plot_fname=None):
    e = evoked.copy().pick(ch_picks)

    try:
        mmn_ch, mmn_lat, mmn_amp = e.get_peak(
            tmin=0.07, tmax=0.25, mode="neg", return_amplitude=True
        )

        # calculate MMN mean amplitude
        e_mean_crop = e.copy().crop(
            tmin=mmn_lat + mean_window[0], tmax=mmn_lat + mean_window[1]
        )
        mmn_mean_amp = e_mean_crop.data.mean() * 1e6
    except ValueError:
        mmn_ch, mmn_lat, mmn_amp, mmn_mean_amp = np.nan, np.nan, np.nan, np.nan

    try:
        p3_ch, p3_lat, p3_amp = e.get_peak(
            tmin=0.15, tmax=0.49, mode="pos", return_amplitude=True, strict=False
        )

        # calculate P3 mean amplitude
        e_mean_crop = e.copy().crop(
            tmin=p3_lat + mean_window[0], tmax=p3_lat + mean_window[1]
        )
        p3_mean_amp = e_mean_crop.data.mean() * 1e6
    except ValueError:
        p3_ch, p3_lat, p3_amp, p3_mean_amp = np.nan, np.nan, np.nan, np.nan

    ret = {
        "mmn_peak_ch": mmn_ch,
        "mmn_peak_lat": mmn_lat,
        "mmn_peak_amp": mmn_amp * 1e6,
        "mmn_mean_amp": mmn_mean_amp,
        "p3_peak_ch": p3_ch,
        "p3_peak_lat": p3_lat,
        "p3_peak_amp": p3_amp * 1e6,
        "p3_mean_amp": p3_mean_amp,
    }

    return ret


participant_peaks(evokeds["pitch"]["harmonic"]["mmn"][2])
# %%
d_list = []
for feature in features:
    for condition in conditions:
        for p in np.array(participants) - 1:
            d = participant_peaks(evokeds[feature][condition]["mmn"][p])
            d["feature"] = feature
            d["condition"] = condition
            d["pid"] = p
            d_list.append(pd.DataFrame(d, index=[0]))


df = pd.concat(d_list, ignore_index=True)
# drop to csv
df.to_csv("../results/peak_measures.csv")
# %%
df.groupby(["feature", "condition"])["pid"].count()
# %%
# plot
pal = {"harmonic": "green", "inharmonic": "red", "changing": "orange"}

g = sns.FacetGrid(df, row="feature", aspect=11 / 8)
g.map_dataframe(
    sns.swarmplot,
    x="condition",
    y="mmn_mean_amp",
    color="black",
    alpha=0.5,
    dodge=False,
)
g.map_dataframe(
    sns.boxplot,
    x="condition",
    y="mmn_mean_amp",
    hue="condition",
    palette="bright",
    dodge=False,
)

# %%
sel_cols = ["mmn_mean_amp", "mmn_peak_lat", "pid", "feature", "condition"]
df_to_melt = df.loc[:, sel_cols]
melted_df = pd.melt(df_to_melt, ["pid", "feature", "condition"])
g = sns.FacetGrid(melted_df, row="feature", col="variable", aspect=11 / 8, sharey=False)
g.map_dataframe(
    sns.swarmplot,
    x="condition",
    y="value",
    color="black",
    alpha=0.8,
    dodge=False,
    size=3,
)
g.map_dataframe(
    sns.boxplot,
    x="condition",
    y="value",
    hue="condition",
    palette=colors,
    dodge=False,
)
plt.savefig("../results/peak_measures.png", dpi=300)


