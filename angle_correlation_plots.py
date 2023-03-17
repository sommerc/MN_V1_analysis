import os
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import colors as mpl_colors
from tqdm.auto import tqdm, trange

from shared import settings


def plot_by_stage(cfg):
    OUT_DIR = cfg["AREA_EXPLORED_OUTDIR"]
    TAB = pd.read_csv(f"{OUT_DIR}/angle_correlation_res.tab", sep="\t", index_col=0)

    STAGES = TAB.Genotype.unique()

    for stg in STAGES:
        tab_sub = TAB[(TAB.Stage == stg)]
        if len(tab_sub) > 0:
            for feature in ["corr_median", "corr_std", "corr_skewness"]:
                f, ax = plt.subplots(figsize=(14, 4))
                a = sns.boxenplot(
                    y=feature,
                    x="Genotype",
                    data=tab_sub,
                    ax=ax,
                    hue="Genotype",
                    box_kws={"alpha": 0.4},
                    dodge=False,
                )
                a.legend_.remove()
                b = sns.stripplot(
                    y=feature,
                    x="Genotype",
                    data=tab_sub,
                    ax=ax,
                    hue="Genotype",
                    dodge=False,
                    zorder=1,
                    legend=False,
                )
                sns.despine(ax=ax)
                ax.set_title(f"{stg} {feature}")
                plt.savefig(f"{OUT_DIR}/{stg}_{feature}.pdf", bbox_inches="tight")
                plt.close(f)


def plot_by_geno(cfg):
    OUT_DIR = cfg["AREA_EXPLORED_OUTDIR"]
    TAB = pd.read_csv(f"{OUT_DIR}/angle_correlation_res.tab", sep="\t", index_col=0)

    GENO = TAB.Genotype.unique()

    for gen in GENO:
        tab_sub = TAB[(TAB.Genotype == gen)]
        if len(tab_sub) > 0:
            for feature in ["corr_median", "corr_std", "corr_skewness"]:
                f, ax = plt.subplots(figsize=(14, 4))
                a = sns.boxenplot(
                    y=feature,
                    x="Stage",
                    data=tab_sub,
                    ax=ax,
                    hue="Stage",
                    box_kws={"alpha": 0.4},
                    dodge=False,
                )
                a.legend_.remove()
                b = sns.stripplot(
                    y=feature,
                    x="Stage",
                    data=tab_sub,
                    ax=ax,
                    hue="Stage",
                    dodge=False,
                    zorder=1,
                    legend=False,
                )
                sns.despine(ax=ax)
                ax.set_title(f"{gen} {feature}")
                plt.savefig(f"{OUT_DIR}/{gen}_{feature}.pdf", bbox_inches="tight")
                plt.close(f)


def plot(cfg):
    plot_by_geno(cfg)
    plot_by_stage(cfg)


if __name__ == "__main__":
    cfg = settings()

    plot(cfg)
