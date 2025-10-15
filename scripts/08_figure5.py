# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
import seaborn as sns

# %%
# load data
p3_predictions = pd.read_csv("../modelling_analysis/output/p3_amp/model_predictions.csv")
peak_measures_df = pd.read_csv('../modelling_analysis/analysis/analysis_dataset.csv')
curve_y_p3 = p3_predictions.groupby('jitter_support_log10')['y'].mean()
x_p3 = curve_y_p3.index

# model parameters
linear_model = {'intercept': 0.4155487,
                'slope': 0.9358146}
sigmoid_model = {'L':-1.310175,
                 'I_0': -1.176047,
                 'k': 6.244479}

data_means = peak_measures_df.groupby('jitter').agg({'jitter_no': 'mean',
                                         'jitter_value': 'mean',
                                         'jitter_support_log10': 'mean',
                                         'mmn_amp': ['mean', 'std', 'size'],
                                         'p3_amp': ['mean', 'std', 'size']
                                         }).reset_index()


t_95quant = t.isf(0.025, 34)
standard_error_mmn = data_means[("mmn_amp", "std")]/np.sqrt(data_means[("mmn_amp", "size")])
standard_error_p3 = data_means[("p3_amp", "std")]/np.sqrt(data_means[("p3_amp", "size")])
data_means[("mmn_amp","CI95_LL")] = data_means[("mmn_amp", "mean")] - t_95quant*standard_error_mmn
data_means[("mmn_amp","CI95_UL")] = data_means[("mmn_amp", "mean")] + t_95quant*standard_error_mmn
data_means[("p3_amp","CI95_LL")] = data_means[("p3_amp", "mean")] - t_95quant*standard_error_p3
data_means[("p3_amp","CI95_UL")] = data_means[("p3_amp", "mean")] + t_95quant*standard_error_p3


# %%

x = np.linspace(-2, -0.6, 1000)


curve_y_mmn = sigmoid_model["L"]/(1 + (np.exp(sigmoid_model["k"] * (x - sigmoid_model["I_0"]))))


# start plotting
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(12, 9), sharey=False, sharex=False)

# plot whiskers for mmn means
# ax[0][0].errorbar(x=data_means["jitter"],
#                y = data_means[("mmn_amp", "mean")],
#                yerr=t_95quant*standard_error_mmn,
#                capsize=10,
#                fmt="o",
#                color="black")

# # plot whiskers for p3a means
# ax[0][1].errorbar(x=data_means["jitter"],
#                y = data_means[("p3_amp", "mean")],
#                yerr=t_95quant*standard_error_p3,
#                capsize=10,
#                fmt="o",
#                color="black")

# boxplots for means
sns.boxplot(peak_measures_df, x='jitter', y='mmn_amp', ax=ax[0][0], palette='viridis')
sns.boxplot(peak_measures_df, x='jitter', y='p3_amp', ax=ax[0][1], palette='viridis')

# calculate threshold value (tipping point)
y_p3_d = np.diff(curve_y_p3)
p3_tipping = x_p3[(y_p3_d > 0).sum()]
mmn_tipping = sigmoid_model['I_0']

# stars
# ax[0][0].annotate("**", xy=("j7", data_means.loc[7, ("mmn_amp", "CI95_UL")]), ha="center")
# ax[0][0].annotate("**", xy=("j6", data_means.loc[6, ("mmn_amp", "CI95_UL")]), ha="center")
# ax[0][0].annotate("**", xy=("j5", data_means.loc[5, ("mmn_amp", "CI95_UL")]), ha="center")


# mmn single observations
for pid in peak_measures_df["pid"].unique():
    this_data = peak_measures_df.loc[peak_measures_df["pid"] == pid, :]
    ax[1][0].plot(this_data["jitter_support_log10"], this_data["mmn_amp"], "-", alpha=0.5, linewidth=1)

# p3 single observations
for pid in peak_measures_df["pid"].unique():
    this_data = peak_measures_df.loc[peak_measures_df["pid"] == pid, :]
    ax[1][1].plot(this_data["jitter_support_log10"], this_data["p3_amp"], "-", alpha=0.5, linewidth=1)

# mmn model prediction
ax[1][0].plot(x, curve_y_mmn, color="black", linewidth=2)

# p3 model prediction
ax[1][1].plot(x_p3, curve_y_p3, color="black", linewidth=2)

# vlines for jitters 
jits = [f'j{n}' for n in range(1,8)]
for v, j in zip(peak_measures_df['jitter_support_log10'].unique()[1:], jits):
    ax[1][0].axvline(v, ls='--', c='grey', lw=1)
    ax[1][1].axvline(v, ls='--', c='grey', lw=1)
    ax[1][0].annotate(j, (v+.01, -4.5))
    ax[1][1].annotate(j, (v+.01, -3))

ax[1][0].axvline(mmn_tipping, ls='--')
ax[1][1].axvline(p3_tipping, ls='--')

# labels
ax[0][0].set_xlabel("experimental condition")
ax[0][1].set_xlabel("experimental condition")
ax[0][0].set_ylabel("MMN amplitude")
ax[0][1].set_ylabel("P3a amplitude")

ax[1][0].set_xlabel("differential entropy of the jitter distribution")
ax[1][1].set_xlabel("differential entropy of the jitter distribution")
ax[1][0].set_ylabel("MMN amplitude")
ax[1][1].set_ylabel("P3a amplitude")

# titles
ax[0][0].set_title("A", loc="left")
ax[0][1].set_title("B", loc="left")
ax[1][0].set_title("C", loc="left")
ax[1][1].set_title("D", loc="left")

plt.savefig('../results/figures/fig5.png', dpi=300)
plt.show()
# %%
mmn_tipping
# %%
p3_tipping
# %%
