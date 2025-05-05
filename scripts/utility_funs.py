import numpy as np
import mne
from scipy.signal import find_peaks

front_channel_picks = ["Fz", "F1", "F2", "AF3", "AF4", "AFz", "F3", "F4", "FC1", "FC2", "FCz"]

def participant_fname(pid):
    """Return a filename for given participant id."""
    # return participants[pid]
    return f'hm_{pid}'


def recode_events(ev):
    # get triggers from events array
    trigs = ev[:, 2]

    # iterate over trigs
    for i, t in enumerate(trigs):

        # always ignore first 10 sounds in the block
        if t > 200 and t < 300:
            trigs[i:i+10] = 0

        # if deviant, set new trigger encoding
        elif t > 100 and t < 200:
            trigs[i] += 1000
            trigs[i+1] += 1200
            trigs[i+2] += 1300

    # put everything back
    ev[:, 2] = trigs
    return ev


def read_and_epoch(fname, ch_eog, ch_exclude=None, inspect=False, bandpass_low=.2, bandpass_high=30, notch=50):
    raw = mne.io.read_raw(fname,
                      eog=ch_eog,
                      # misc=ch_ecg,
                      exclude=ch_exclude,
                      stim_channel='Status',
                      preload=True)

    raw.set_montage('biosemi64')

    # filter
    raw.notch_filter(notch)
    raw.filter(bandpass_low, bandpass_high)

    # visual inspection
    if inspect:
        raw.plot()

    # epoch the data
    events_raw = mne.find_events(raw, stim_channel='Status')
    events = recode_events(events_raw)
    event_ids = {f'j{i}/std': i+1 for i in range(8)}
    event_ids.update({f'j{i}/dev_1': i+1101 for i in range(8)})
    event_ids.update({f'j{i}/dev_2': i+1201 for i in range(8)})
    event_ids.update({f'j{i}/dev_3': i+1301 for i in range(8)})
    epochs = mne.Epochs(raw,
                        events,
                        event_ids,
                        tmin=-.1, tmax=.5,
                        baseline=None,
                        decim=2 # decimate so new sr is 1024
                        )
    
    return raw, epochs


def read_preprocessed_epochs(pid, epochs_path):
    epochs = mne.read_epochs(f'{epochs_path}/{pid}-epo.fif')
    return epochs



def make_evokeds(epochs):
    jitters = [f'j{i}' for i in range(8)]
    evokeds = {}

    for jitter in jitters:
        evokeds[jitter] = {
            'std': epochs[f'{jitter}/std'].average(),
            'dev': epochs[f'{jitter}/dev'].average(),
        }
        evokeds[jitter]['mmn'] = mne.combine_evoked([evokeds[jitter]['dev'], evokeds[jitter]['std']], weights=[1, -1])

    return evokeds



def participant_peaks(evoked, mean_window=(-0.025, 0.025)):
    e = evoked.copy().pick(front_channel_picks)
    p3_window = (.15, .35)
    mmn_window = (.07, .25)
    try:
        # numpy array of mmn window data
        mmn_epoch = e.copy().crop(*mmn_window)
        e_times = mmn_epoch.times
        np_epoch = np.mean(mmn_epoch.get_data(), axis=0)

        # find negative peaks (cause it's mmn)
        peak_indices, _ = find_peaks(-np_epoch)
        peak_index = np.argmin(np_epoch[peak_indices])
        mmn_lat = e_times[peak_indices[peak_index]]
        
        # calculate MMN mean amplitude
        e_mean_crop = e.copy().crop(
            tmin=mmn_lat + mean_window[0], tmax=mmn_lat + mean_window[1]
        )
        mmn_amp = e_mean_crop.data.mean() * 1e6

    except ValueError:
        mmn_lat, mmn_amp = np.nan, np.nan


    try:
        # numpy array of mmn window data
        p3_epoch = e.copy().crop(*p3_window)
        e_times = p3_epoch.times
        np_epoch = np.mean(p3_epoch.get_data(), axis=0)

        # find negative peaks (cause it's mmn)
        peak_indices, _ = find_peaks(np_epoch)
        peak_index = np.argmax(np_epoch[peak_indices])
        p3_lat = e_times[peak_indices[peak_index]]

        # calculate P3 mean amplitude
        e_mean_crop = e.copy().crop(
            tmin=p3_lat + mean_window[0], tmax=p3_lat + mean_window[1]
        )
        p3_amp = e_mean_crop.data.mean() * 1e6

    except ValueError:
        p3_lat, p3_amp = np.nan, np.nan

    ret = {
        "mmn_lat": mmn_lat,
        "mmn_amp": mmn_amp,
        "p3_lat": p3_lat,
        "p3_amp": p3_amp,
    }

    return ret


def orn_peaks(evoked, mean_window=(-0.025, 0.025)):
    e = evoked.copy().pick(front_channel_picks)
    try:
        orn_ch, orn_lat, orn_amp = e.get_peak(
            tmin=0.1, tmax=0.3, mode="neg", return_amplitude=True
        )
        # calculate ORN mean amplitude
        e_mean_crop = e.copy().crop(
            tmin=orn_lat + mean_window[0], tmax=orn_lat + mean_window[1]
        )
        orn_mean_amp = e_mean_crop.data.mean() * 1e6
    except ValueError:
        orn_ch, orn_lat, orn_amp, orn_mean_amp = np.nan, np.nan, np.nan, np.nan

    ret = {
        "orn_peak_ch": orn_ch,
        "orn_peak_lat": orn_lat,
        "orn_peak_amp": orn_amp * 1e6,
        "orn_mean_amp": orn_mean_amp,
    }
    return ret


def p2_peaks(evoked, peak_time, mean_window=(-0.025, 0.025)):
    e = evoked.copy().pick(front_channel_picks)
    tmin, tmax = peak_time + mean_window[0], peak_time + mean_window[1]
    p2_amp = e.copy().crop(tmin, tmax).data.mean() * 1e6

    return p2_amp