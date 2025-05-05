# %%
import mne
from autoreject import AutoReject
import utility_funs as uf
from sys import argv


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
    
# %%

# read raw data and epoch
_, epochs = uf.read_and_epoch(fname, ch_eog, ch_exclude)


# %%
epochs.load_data()
# %%
# Run autoreject (first before the ICA)

ar = AutoReject(n_interpolate=[1, 4, 8, 16], n_jobs=n_jobs)
ar.fit(epochs)
# %%
ar.save(f'{ar_path}/{p}-ar.hdf5', overwrite=True)
# %%
epochs_ar, reject_log_1 = ar.transform(epochs, return_log=True)

# store autoreject reject log 1 in a file
reject_log_1.save(f"{ar_path}/{p}-rl1.npz", overwrite=True)

# %%
# ICA

# compute ica
ica = mne.preprocessing.ICA(
    n_components=30, 
    max_iter='auto', 
    random_state=97
    )

# fit ICA to ar-ed data
ica.fit(epochs_ar)

# save ica solution to file
ica.save(f'{ica_path}/{p}-ica.fif', overwrite=True)

# %%
