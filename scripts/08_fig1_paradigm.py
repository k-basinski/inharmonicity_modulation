# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import soundfile as sf

# %%
# config
soundpool_location = "../paradigms/eeg/soundpool_eeg/"

rng = np.random.default_rng()


def load_sound(freqs, jitters, ns, channel=0):
    ioi = 0.07

    sound_list = []
    for f, j, n in zip(freqs, jitters, ns):
        # open sound
        sound, fs = sf.read(f"{soundpool_location}f{f}_j{j}_n{n}.wav")

        # pad the sound so the ioi is 100 ms.
        pad_width = int((fs * ioi) - sound.shape[0])
        sound_padded = np.pad(sound, ((0, pad_width), (0, 0)))
        sound_mono = sound_padded[:, channel]
        sound_list.append(sound_mono)

    return np.concatenate(sound_list)


def get_fs():
    """Look at a sample file to get the sample rate."""
    _, fs = sf.read(f"{soundpool_location}f200_j0_n0.wav")
    return fs


# %%
fs = get_fs()
# spectra
frequencies = [400] * 7 + [500] * 3
jitters_h = [0] * 10
jitters_ih = [5] * 10
ns = rng.integers(0, 1000, 10)

sig_h = load_sound([400], [0], ns, 0)[int(fs * 0.02) : int(fs * 0.022)]
sig_ih = load_sound([400], [7], ns, 0)[int(fs * 0.02) : int(fs * 0.022)]

freq_ticks = [500, 1000, 2000, 5000, 10000, 20000]
freq_labels = [500, "1k", "2k", "5k", "10k", "20k"]


time_vector = np.arange(len(sig_h)) / fs

fig, axs = plt.subplots(ncols=3, nrows=2, figsize=(12, 7), sharey=False)

panel_labels = "ABCDEFGH"


# roving
# build df
c = [1, 2, 2, 3, 3, 1, 2, 2, 3, 3, 3, 3, 1, 2, 2, 3, 3, 3, 3, 3, 1, 2, 2, 3, 3]
df = pd.DataFrame(
    {
        "Sound #": np.arange(0, 25) * 0.6,
        "Fundamental frequency (Hz)": ([250] * 5 + [500] * 7 + [350] * 8 + [450] * 5),
        "Class": c,
    }
)
df["Class"] = df["Class"].replace({1: "deviant", 2: "excluded", 3: "standard"})


sns.scatterplot(
    df,
    x="Sound #",
    y="Fundamental frequency (Hz)",
    hue="Class",
    marker=">",
    palette=["red", "grey", "blue"],
    ax=axs[0][0],
)
axs[0][0].set_xlabel("Time (s)")
axs[0][0].set_title("A", loc="left")
axs[0][0].set_ylim(190, 510)

# behavioral
axs[0][1].scatter([0, 0.5], [300, 350], marker=">")
axs[0][1].set_xlim(-0.3, 3)
axs[0][1].set_ylim(190, 510)
axs[0][1].annotate("Was the second sound \nhigher or lower \nin pitch?", (0.8, 400))
axs[0][1].set_xlabel("Time (s)")
axs[0][1].set_ylabel("Fundamental f|requency (Hz)")
# axs[0][1].set_xticks([])
axs[0][1].set_title("B", loc="left")

# spectra - all jitters
sig = load_sound(frequencies, list(range(8)), rng.integers(0, 1000, 8), 0)
Pxx, freqs, bins, im = axs[0][2].specgram(sig, NFFT=3360, Fs=fs)
axs[0][2].set_yscale("log")
axs[0][2].set_ylim(380, 5000)
xtick_times = np.linspace(0.035, 0.505, 8)
xtick_labels = np.arange(8)
axs[0][2].set_yticks(freq_ticks, freq_labels)
axs[0][2].set_xticks(xtick_times, xtick_labels)
axs[0][2].set_xlabel("Jitter")
axs[0][2].set_ylabel("Frequency (Hz)")
axs[0][2].set_title("C", loc="left")


xtick_times = np.linspace(0, 0.61, 10)
xtick_labels = np.arange(1, 11)

# spectra
for i, col in enumerate([0, 4, 7]):
    sig = load_sound(frequencies, [col] * 10, ns, 0)
    Pxx, freqs, bins, im = axs[1][i].specgram(sig, NFFT=3360, Fs=fs)
    axs[1][i].set_yscale("log")
    axs[1][i].set_ylim(400, 10000)
    axs[1][i].set_yticks(freq_ticks, freq_labels)
    axs[1][i].set_xticks(xtick_times, xtick_labels)
    axs[1][i].set_ylabel("Frequency (Hz)")
    axs[1][i].set_title(f"{panel_labels[i + 3]}", loc="left")
    axs[1][i].axvline(xtick_times[7], c="red", linestyle="--")
    axs[1][i].set_xlabel("Sound #")

plt.tight_layout()
plt.savefig("../results/figures/fig1.png", dpi=300)

# %%
