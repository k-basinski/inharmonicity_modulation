# %%
import pandas as pd
import numpy as np
from psychopy import data

# %%
pids = [

    303,
    309,
    310,
    312,
    314,
    315,
    317,
    318,
    319,
    320,
    321,
    322,
    323,
    324,

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

    341,
    342,
    404,
    406,
    407,
    408,
]


flist = [f"p{i}_log.csv" for i in pids]

ddf_list = []

for i, f in enumerate(flist):
    ddf = pd.read_csv(f)
    ddf["pid"] = pids[i]
    ddf_list.append(ddf)

df = pd.concat(ddf_list, ignore_index=True)

# assume all incorrect
df["correct"] = 0

# change correct values
sel = ((df.responses == "up") & (df.targets == "higher")) | (
    (df.responses == "down") & (df.targets == "lower")
)
df.loc[sel, "correct"] = 1
# %%

halts_array = []

for pid in pids:

    # get single participant data
    single = df.loc[df.pid == pid, :]

    sim_results = []
    halts = []
    generator_df = single.iterrows()
    for idx, r in generator_df:
        # assume first row is the start of the first staircase
        start_value = r["jitter"]

        # define staircase as in original experiment
        staircase = data.StairHandler(
            startVal=start_value,
            stepType="lin",
            nReversals=6,
            stepSizes=[1],
            minVal=0,
            maxVal=10,
            nUp=3,
            nDown=1,
            nTrials=1,
        )
        staircase_start = True

        # run staircase
        for stair in staircase:
            # yield new df row
            if not staircase_start:
                try:
                    idx, r = next(generator_df)
                except StopIteration:
                    break

            # check if correct
            if r["correct"] == 1:
                thisResp = -1
            else:
                thisResp = 1

            # plug into staircase
            staircase.addData(thisResp)

            # log everything
            sim_results.append(
                {
                    "sim_jitter": stair,
                    "log_jitter": r["jitter"],
                    "thisResponse": thisResp,
                    "staircase_start": staircase_start,
                    "id": r.iloc[0],
                }
            )

            # change to false when not first iteration
            staircase_start = False



    sim_df = pd.DataFrame(sim_results)
    sim_df["jitter_check"] = (sim_df.sim_jitter == sim_df.log_jitter)

    # detect halts
    halt_indices = np.array(sim_df[sim_df.staircase_start].index - 1)

    # check if all checks are okay
    print(f'Checking participant {pid}...')
    if len(sim_df) != sim_df.jitter_check.sum():
        print(f"Simulated jitters check failed! {sim_df.jitter_check.sum()}/{len(sim_df)} correctly simulated jitters.")

    if halt_indices[0] != -1:
        print('First halt not at 0!')

    if len(halt_indices) != 15:
        print(f'{len(halt_indices)} halts detected (instead of 15)!')

    print()


    # re-point -1 to last index
    halt_indices[0] = sim_df.index[-1]

    # get jitters at halt points
    halts = sim_df.copy().iloc[halt_indices]
    halts['pid'] = pid

    halts_array.append(halts)

# %%
halts_df = pd.concat(halts_array)
halts_df[['pid', 'log_jitter', 'id']].to_csv('halts.csv')
halts_df
# %%
halts_df.log_jitter.mean().round(2)
# %%
halts_df.log_jitter.std().round(2)
# %%
halts_df.groupby(['pid']).log_jitter.mean().hist()
# %%
