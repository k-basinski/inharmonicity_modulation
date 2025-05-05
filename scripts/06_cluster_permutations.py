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

# load evoked potentials
f = open("../results/evokeds.p", "rb")
ev = pickle.load(f)
f.close()

# %%
# cluster based permutations - presence of oddball responses
# get standards


def evoked_ndarrays(evoked, jitters, conds):
    evoked_arrays = {}
    for jit in jitters:
        evoked_arrays[jit] = {}
        for cond in conds:
            # extract values to ndarray
            res = np.array([i.get_data() for i in evoked[jit][cond]])

            # transpose to fit cluster function requirements
            res_t = np.transpose(res, (0, 2, 1))

            # write out to evoked_arrays dict
            evoked_arrays[jit][cond] = res_t

    return evoked_arrays


def cluster_permutations(a, b, adjacency, n_perm=1024, threshold_tfce=None):
    cluster_stats = mne.stats.spatio_temporal_cluster_1samp_test(
        a - b,
        n_permutations=n_perm,
        tail=0,
        threshold=threshold_tfce,
        n_jobs=-1,
        adjacency=adjacency,
        out_type="mask",
    )
    return cluster_stats


def print_sig_clusters(cluster_stats, p_thresh=0.05):
    F_obs, clusters, pvals, _ = cluster_stats
    samples_in_epoch = 615
    # make times vector
    times = (np.arange(samples_in_epoch) * 1 / 1024) - 0.1

    for c in range(len(clusters)):
        if pvals[c] < p_thresh:
            print(f"Cluster {c}, p = {pvals[c]}")
            t_start = times[np.any(clusters[c], axis=1)][0]
            t_stop = times[np.any(clusters[c], axis=1)][-1]
            no_sensors = np.max(clusters[c].sum(axis=1))
            print(f"{round(t_start, 3)} - {round(t_stop, 3)}")
            print(f"Sensors {no_sensors}/30")
            print()
            

jitters = [f"j{i}" for i in range(8)]
conditions = ['std', 'dev_1', 'dev_2', 'dev_3', 'mismatch_1', 'mismatch_2', 'mismatch_3', 'orn_standards', 'orn_deviants']

# get adjacency matrix
adjacency, ch_names = mne.channels.read_ch_adjacency("biosemi64")


evoked_arrays = evoked_ndarrays(ev, jitters, ["std", "dev_1"])

cluster_list = []
for j in jitters:
    res = cluster_permutations(
        evoked_arrays[j]["std"], evoked_arrays[j]["dev_1"], adjacency,
        threshold_tfce=dict(start=0, step=0.2)
    )
    cluster_list.append(res)

# %%

def get_significant_times(cluster, threshold = .05):
    pv = cluster[2]
    # make times vector
    o = np.array(res[1])[pv < threshold]
    sig_times = np.any(o, axis=(0, 2))
    return sig_times


def visualize_clusters(cluster_list):
    samples_in_epoch = 615
    times = (np.arange(samples_in_epoch) * 1 / 1024) - 0.1
    how_many_clusters = len(cluster_list)
    fig, axs = plt.subplots(nrows=how_many_clusters, sharex=True, figsize=(6, how_many_clusters))
    for i, c in enumerate(cluster_list):
        cluster_times = get_significant_times(c)
        axs[i].plot(times, cluster_times)
        axs[i].set_title(f'jitter {i}')
    
    fig.tight_layout()
    fig.show()

visualize_clusters(cluster_list)
# %%
