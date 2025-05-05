# %%
import mne
import utility_funs as uf
from sys import argv
from autoreject import AutoReject

# config
# load data and set channel names, montage
data_dir = '/Users/kbas/sci_data/harmonicity_modulation/'
p = int(argv[1])
data_id = uf.participant_fname(p)

fname = data_dir + data_id + '.bdf'
ar_path = '../results/autoreject'
ica_path = '../results/ica/'
ch_eog = ['EXG1', 'EXG2']

ch_exclude = [f'EXG{i}' for i in range(3,9)]

# set n_jobs via argv or default to -1
if len(argv) >= 3:
    n_jobs = int(argv[2])
else:
    n_jobs = -1

# read raw data and epoch
raw, epochs = uf.read_and_epoch(fname, ch_eog, ch_exclude)
epochs.load_data()
# load ICA
ica = mne.preprocessing.read_ica(f"{ica_path}/{p}-reviewed-ica.fif")

# %%
# apply ICA
epochs_after_ica = ica.apply(epochs)

# %%
# apply autoreject again, this time to the actual data and save
print("\n\n Running autoreject 2nd time...\n")

ar2 = AutoReject(n_interpolate=[1, 4, 8, 16], n_jobs=n_jobs)
epochs_ar_2, reject_log_2 = ar2.fit_transform(epochs_after_ica, return_log=True)

# store autoreject reject log 1 in a file
reject_log_2.save(f'{ar_path}/{p}-rl2.npz', overwrite=True)



# re-reference to mastoids
epochs_ar_2.set_eeg_reference(['P9', 'P10'])

# baseline correct the epochs
epochs_ar_2.apply_baseline((-0.1, 0))

# save to filepath
epochs_ar_2.save(f"{data_dir}/preprocessed/{p}-epo.fif", overwrite=True)

print(f"Participant {p} saved successfully.")
# %%
