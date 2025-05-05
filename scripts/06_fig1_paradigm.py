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


# spectra
frequencies = [400] * 7 + [500] * 3
jitters_h = [0] * 10
jitters_ih = [5] * 10
ns = rng.integers(0, 1000, 10)

sig_h = load_sound(frequencies, jitters_h, ns, 0)
sig_ih = load_sound(frequencies, jitters_ih, ns, 0)

fs = get_fs()
freq_ticks = [500, 1000, 2000, 5000, 10000, 20000]
freq_labels = [500, "1k", "2k", "5k", "10k", "20k"]
time_ticks = [0.005, 0.01, 0.015, 0.02]
time_labels = [5, 10, 15, 20]
time_vector = np.arange(len(sig_h)) / fs

fig, axs = plt.subplots(ncols=8, nrows=1, figsize=(20, 6), sharey=True)

for col in range(8):
    sig = load_sound(frequencies, [col] * 10, ns, 0)
    Pxx, freqs, bins, im = axs[col].specgram(sig, NFFT=3360, Fs=fs)
    axs[col].set_yscale("log")
    axs[col].set_ylim(400, 20000)
    axs[col].set_yticks(freq_ticks, freq_labels)
    if col == 0:
        axs[col].set_ylabel("Frequency (Hz)")
    axs[col].set_title(f"Jitter={col}")
    axs[col].axvline(7 * 0.07, c="red", linestyle="--")

plt.tight_layout()
plt.savefig("../results/figures/fig1.png", dpi=300)

# %%
