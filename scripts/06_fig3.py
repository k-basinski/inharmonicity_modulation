# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

peaks = pd.read_csv('../results/csv/mismatch_peaks.csv')
# %%
m1_peaks = peaks[peaks.mismatch == 'mismatch_1']
m1_peaks

# %%
fig, axs =plt.subplots(ncols=2, nrows=2, figsize=(12,8), sharex=True)

# mmn amplitude
sns.violinplot(m1_peaks, x='jitter', y='mmn_amp', ax=axs[0][0])
sns.lineplot(
        m1_peaks, x='jitter', y='mmn_amp',
        units="pid",
        estimator=None,
        alpha=0.2,
        color="black",
        linewidth=0.5,
        ax=axs[0][0]
    )
axs[0][0].axhline(0, c='red', ls='--')
axs[0][0].set_ylabel("MMN amplitude (\u03BCV)")
axs[0][0].set_xlabel(None)


# mmn latency
sns.violinplot(m1_peaks, x='jitter', y='mmn_lat', ax=axs[0][1])
sns.lineplot(
        m1_peaks, x='jitter', y='mmn_lat',
        units="pid",
        estimator=None,
        alpha=0.2,
        color="black",
        linewidth=0.5,
        ax=axs[0][1]
    )
axs[0][1].set_ylabel("MMN latency (s)")
axs[0][1].set_xlabel(None)

# p3 amplitude
sns.violinplot(m1_peaks, x='jitter', y='p3_amp', ax=axs[1][0])
sns.lineplot(
        m1_peaks, x='jitter', y='p3_amp',
        units="pid",
        estimator=None,
        alpha=0.2,
        color="black",
        linewidth=0.5,
        ax=axs[1][0]
    )
axs[1][0].axhline(0, c='red', ls='--')
axs[1][0].set_ylabel("P3 amplitude (\u03BCV)")


# p3 latency
sns.violinplot(m1_peaks, x='jitter', y='p3_lat', ax=axs[1][1])
sns.lineplot(
        m1_peaks, x='jitter', y='p3_lat',
        units="pid",
        estimator=None,
        alpha=0.2,
        color="black",
        linewidth=0.5,
        ax=axs[1][1]
    )
axs[1][1].set_ylabel("P3 latency (s)")

fig.tight_layout()

plt.savefig('../results/figures/fig3.png', dpi=300)
plt.show()

# %%
