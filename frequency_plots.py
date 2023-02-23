import os
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import colors as mpl_colors
from tqdm.auto import tqdm, trange

from shared import settings


if __name__ == "__main__":
    cfg = settings()
    STAGES = [
        "37-38",
        "44-48",
        "52-54",
        "57-58",
        "59-62",
        "63-64",
        "Juv",
    ]
    OUT_DIR = cfg["FREQUENCY_OUTDIR"]

    for STAGE in STAGES:
        cfgs = cfg[STAGE]
        if "FREQ_FOR" in cfgs:
            for name, nodes in cfgs["FREQ_FOR"].items():
                tab_stg_freq = pd.read_csv(
                    f"{cfg['FREQUENCY_OUTDIR']}/frequency_{STAGE}_{name}_res.tab",
                    sep="\t",
                    index_col=0,
                )

                _, tail_ptn, _ = nodes

                f, ax = plt.subplots(
                    1, tab_stg_freq.Genotype.nunique(), sharey=True, figsize=(20, 4)
                )
                cc = ax[0]._get_lines.prop_cycler
                for i, (gen, tab) in enumerate(tab_stg_freq.groupby("Genotype")):
                    a = tab.T.iloc[6:].mean(1)
                    b = tab.T.iloc[6:].std(1)
                    x_vals = a.index.astype("float")
                    color = next(cc)["color"]
                    ax[i].plot(x_vals, a, color=color)
                    ax[i].fill_between(x_vals, (a - b), (a + b), alpha=0.3, color=color)
                    ax[i].set_title(gen)
                    ax[i].set_ylim(0, 10)
                    sns.despine(ax=ax[i])
                    ax[i].set_xlabel(f"Frequency of angle change at {tail_ptn}")
                    ax[i].set_ylabel("Mean CWT power spectrum")
                plt.tight_layout()

                plt.savefig(f"{OUT_DIR}/cwt_mean_ps_{STAGE}_{name}_{tail_ptn}.pdf")

                feature = "dominant_freq"
                f, ax = plt.subplots(figsize=(14, 4))

                b = sns.stripplot(
                    y=feature,
                    x="Genotype",
                    data=tab_stg_freq,
                    ax=ax,
                    hue="Genotype",
                    dodge=False,
                    zorder=1,
                    legend=False,
                )
                sns.despine(ax=ax)
                ax.set_title(f"{STAGE}_{name}_{tail_ptn}")
                plt.savefig(
                    f"{OUT_DIR}/dominant_cwt_freq_{STAGE}_{name}_{tail_ptn}.pdf"
                )
