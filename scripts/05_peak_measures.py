# %%
from importlib import reload
import utility_funs as uf
import pandas as pd
import pickle
import matplotlib.pyplot as plt

reload(uf)

jitters = [f"j{i}" for i in range(8)]
mismatches = [f'mismatch_{i}' for i in range(1,4)]

# %%
# load evoked potentials
f = open("../results/evokeds.p", "rb")
ev = pickle.load(f)
f.close()
# %%
# calculate mismatch wave peaks per jitter
peaks_list = []
for jit in jitters:
    for mm in mismatches:
        for pid, e in enumerate(ev[jit][mm]):
            # calculate participant-wise peaks
            peaks = uf.participant_peaks(e)

            # append data to resulting dataframe
            peaks['pid'] = pid
            peaks['jitter'] = jit
            peaks['jitter_no'] = int(jit[1])
            peaks['mismatch'] = mm
            peaks_list.append(peaks)

            # plot individual evoked responses and peak measures for visual inspection
            if mm == 'mismatch_1':
                # Turn interactive plotting off
                plt.ioff()
                fig, ax = plt.subplots()
                # plot evoked responses for each channel
                e.plot(picks=uf.front_channel_picks, show=False, axes=ax)
                # mark MMN peak with vertical line and amplitude  with a red dot
                ax.plot(peaks['mmn_lat'], peaks['mmn_amp'], "ro")
                ax.axvline(peaks['mmn_lat'], c='red')
                ax.axvspan(.07, .25, ymin=0, ymax=0.1, color='red', alpha=.2)
                # mark P3 peak with vertical line and amplitude with a blue dot 
                ax.plot(peaks['p3_lat'], peaks['p3_amp'], "bo")
                ax.axvline(peaks['p3_lat'], c='blue')
                ax.axvspan(.15, .4, ymin=0.9, ymax=1, color='blue', alpha=.2)
                fig.savefig(f"../results/figures/peak_checks/p{pid}_{jit}_peaks.png")
                plt.close()



# export to csv
mismatch_df = pd.DataFrame(peaks_list)
mismatch_df.to_csv('../results/csv/mismatch_peaks.csv')
# %%



