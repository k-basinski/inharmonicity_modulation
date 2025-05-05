# %%
import mne
import utility_funs as uf
from sys import argv

# config
# load data and set channel names, montage
data_dir = '/Users/kbas/sci_data/harmonicity_modulation/'
p = int(argv[1])
data_id = uf.participant_fname(p)

fname = data_dir + data_id + '.bdf'
ar_path = 'autoreject'
ica_path = '../results/ica/'
ch_eog = ['EXG1', 'EXG2']
# ch_ecg = ['EXG3', 'EXG4']
ch_exclude = [f'EXG{i}' for i in range(3,9)]


# read raw data and epoch
raw, epochs = uf.read_and_epoch(fname, ch_eog, ch_exclude)

# load ICA
ica = mne.preprocessing.read_ica(f"{ica_path}/{p}-ica.fif")

# %%

# plotting diagnostics

# find which ICs match the EOG pattern
eog_epochs = mne.preprocessing.create_eog_epochs(raw)
eog_evoked = eog_epochs.average()
eog_indices, eog_scores = ica.find_bads_eog(epochs)


# start with automatically detected EOG and ECG components
# ica.exclude = eog_indices + ecg_indices
ica.exclude = eog_indices 

ica_done = False

while not ica_done:
    # plot ICA components
    ica.plot_components(inst=epochs)

    # plot overlay
    ica.plot_overlay(raw, exclude=ica.exclude)

    # barplot of ICA component "EOG match" scores
    ica.plot_scores(eog_scores)

    # # barplot of ICA component "ECG match" scores
    # ica.plot_scores(ecg_scores, exclude=ecg_indices, title="ECG components")

    # plot ICs applied to the averaged EOG epochs, with EOG matches highlighted
    ica.plot_sources(eog_evoked)

    print(f'\nCurrent picks are {ica.exclude}. You happy? (y/n)')
    if input() == 'y':
        print(f'Fine, saving ICA with picks {ica.exclude}.')
        ica_done = True

# %%
# save ICA solution with updated component picks

# save ica solution to file
ica.save(f'{ica_path}/{p}-reviewed-ica.fif', overwrite=True)
