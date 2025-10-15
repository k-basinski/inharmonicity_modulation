import inharmonicon
import numpy as np
import antropy

jitters = np.geomspace(0.005, .5, 10)[:7]
f0 = 440
f_max = 20000

n_runs=100
entropies = np.zeros((n_runs,7))

for i in range(n_runs):
    sounds = []
    for jitter in jitters:
        this_series = inharmonicon.Harmonics(f0=f0, fmax=20000, jitter_rate=jitter)
        this_sound = inharmonicon.Sound(this_series, length=10)
        sounds.append(this_sound)

    entropies[i] = np.array([antropy.spectral_entropy(sound.sound[:,0], sf=48000, normalize=True) for sound in sounds])
    print(entropies[i])

mean_entropies = np.mean(entropies, axis=0)
print("MEAN")
print(mean_entropies)
