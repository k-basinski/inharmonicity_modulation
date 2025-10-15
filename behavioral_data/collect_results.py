# %%
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
# %%

pids = [
    303, 309, 310, 312, 
    314,315,317,318,319,320,
    321,322,323,324,326,327,328,329,330,
    332,333,334,335,336,
    341,342,404,406,407,408    
]


flist = [f'p{i}_log.csv' for i in pids]

ddf_list = []

for i, f in enumerate(flist):
    ddf = pd.read_csv(f)
    ddf['pid'] = pids[i]
    ddf_list.append(ddf)

df = pd.concat(ddf_list, ignore_index=True)

# assume all incorrect
df['correct'] = 0

# change correct values
sel = ((df.responses == 'up') & (df.targets == 'higher')) | ((df.responses == 'down') & (df.targets == 'lower'))
df.loc[sel, 'correct'] = 1

# collapse by increments
gdf = df.groupby(['pid','jitter'])
summed = gdf.correct.sum()
total = gdf.correct.count()
percentage = summed / total
output = pd.DataFrame({'x': summed.index, 'sum': summed, 'total': total, '%': percentage})
output = output.reset_index()

# recode jitter indexes to true values
jitter_values = np.concatenate([[0], np.geomspace(0.005, .5, 10)])
jitter_indices = list(range(len(jitter_values)))
recode = dict(zip(jitter_indices, jitter_values))
output['levels'] = output['jitter'].replace(recode)
output.to_csv('collected_results.csv')
# %%
sns.boxplot(data=output, x='jitter', y='%')

# %%
