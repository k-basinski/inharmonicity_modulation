# %%

# Load mismatch peak measures data and test if MMMN and P3 
# amplitudes differ from zero. Do that for each jitter and 
# each mismatch (deviant order).

import pandas as pd
import pingouin as png


df = pd.read_csv('../results/csv/mismatch_peaks.csv')

mismatches = [f'mismatch_{i}' for i in range(1,4)]
jitters = [f"j{i}" for i in range(8)]

mismatches = ['mismatch_1']
# iterate
res = []
for m in mismatches:
    for jit in jitters:
        sel = (df.mismatch == m) & (df.jitter == jit)
        test = png.ttest(df[sel].mmn_amp, 0)
        test['mismatch'] = m
        test['jit'] = jit
        res.append(test)

test_results = pd.concat(res)

test_results['p-val'].round(3)

# %%
sel = (df.mismatch == m) & (df.jitter == jit)
df[sel].mmn_mean_amp
# %%
jit
# %%
df
# %%
