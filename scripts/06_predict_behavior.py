# %%
import numpy as np
import pandas as pd
import polars as pl
from pymer4.models import lmer, compare
import seaborn as sns


# %%
# read peak data
peaks = pd.read_csv("../results/csv/mismatch_peaks.csv")

# read behavioral halts data
behavioral_results = pd.read_csv('../behavioral_data/collected_results.csv')

# remap consecutive participant numbering to participant ids (pids)
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

pid_mapping = zip(range(len(participants)), participants)
peaks.pid = peaks.pid.replace(dict(pid_mapping))


# %%
# select relevant columns
columns_select = ['pid', 'jitter', '%']

behavior = behavioral_results.loc[(behavioral_results.jitter <= 7), columns_select]
behavior = behavior.set_index(['pid', 'jitter'])
behavior = behavior.rename(columns={'%': 'perc_correct'})
# %%
peaks_join = peaks.loc[peaks.mismatch == 'mismatch_1', ['pid', 'jitter_no', 'mmn_amp']]
peaks_join = peaks_join.rename(columns={'jitter_no': 'jitter'})
peaks_join = peaks_join.set_index(['pid', 'jitter'])
peaks_join

# join and drop multiindex
behavior_to_pl = behavior.join(peaks_join).reset_index()
behavior_to_pl
# %%
#  convert to polars dataframe
res = pl.DataFrame(behavior_to_pl)
# %%
res
# %%
model0 = lmer('perc_correct ~ (1|pid)', data=res)
model1 = lmer('perc_correct ~ jitter + (1|pid)', data=res)
model2 = lmer('perc_correct ~ jitter + mmn_amp + (1|pid)', data=res)
model3 = lmer('perc_correct ~ jitter * mmn_amp + (1|pid)', data=res)
model0.fit()
model1.fit()
model2.fit()
model3.fit()
# %%
compare(model0, model1, model2, model3)
