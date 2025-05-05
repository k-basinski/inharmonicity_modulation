# %%
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import psignifit as ps
import psignifit.psigniplot as psp
# %%
# load data from csv
df = pd.read_csv('../behavioral_data/collected_results.csv')
# %%
df

# %%
# simple plots
sns.boxplot(data=df, x='jitter', y='%')
plt.hlines(.5, 0, 10, colors='red', linestyles='dashed')
plt.show()

# %%
df.groupby('jitter')['%'].mean()

# %%
# get one participant
pid = 1
sel_columns = ['jitter', 'sum', 'total']
data = df.loc[df.pid == pid, sel_columns].to_numpy()
# data = df.loc[:, sel_columns].to_numpy()
data
# %%
fixed_parameters = {'lambda': 0.02, 'gamma': 0.5}
result = ps.psignifit(
    data,
    experiment_type="2AFC",
    sigmoid="neg_norm",
    # stimulus_range=[0, 10],
    fixed_parameters=fixed_parameters,
)
result.parameter_estimate
# %%
psp.plot_psychometric_function(result)
# %%
data = np.array(
    [
        [10, 74, 107],
        [9, 41, 57],
        [8, 39, 51],
        [7, 27, 39],
        [6, 13, 25],
        [5, 8, 16],
        [4, 10, 17],
        [3, 17, 25],
        [2, 12, 21],
        [1, 14, 23],
        [0, 12, 21],
    ]
)
result = ps.psignifit(
    data,
    experiment_type="2AFC",
    sigmoid="norm",
    fixed_parameters=fixed_parameters,
)
result.parameter_estimate
psp.plot_psychometric_function(result)
# %%
