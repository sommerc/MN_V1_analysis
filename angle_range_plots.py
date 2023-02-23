import numpy as np
import pandas as pd

import seaborn as sns
from matplotlib import pyplot as plt

from shared import settings


def plot_by_stage(cfg):
    TAB = pd.read_csv("angle_range/angle_range_res.tab", sep="\t", index_col=0)

    TAB["angle_std"] = np.rad2deg(TAB["angle_std"])
    TAB["angle_p95-5_dist"] = np.rad2deg(TAB["angle_p95-5_dist"])
    STAGES = [
        "37-38",
        "44-48",
        "52-54",
        "57-58",
        "59-62",
        "63-64",
        "Juv",
    ]

    AR_AT = TAB.angle_at.unique()

    OUT_DIR = cfg["ANGLE_RANGE_OUTDIR"]

    for stg in STAGES:
        for angle_at in AR_AT:
            tab_sub = TAB[(TAB.Stage == stg) & (TAB.angle_at == angle_at)]
            if len(tab_sub) > 0:
                for feature in [
                    "angle_p95-5_dist",
                    "angle_std",
                ]:
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
                    ax.set_title(f"{stg} {angle_at}")
                    plt.savefig(
                        f"{OUT_DIR}/{stg}_{angle_at}_{feature}.pdf",
                        bbox_inches="tight",
                    )
                    plt.close(f)


def plot_by_geno(cfg):
    TAB = pd.read_csv("angle_range/angle_range_res.tab", sep="\t", index_col=0)

    TAB["angle_std"] = np.rad2deg(TAB["angle_std"])
    TAB["angle_p95-5_dist"] = np.rad2deg(TAB["angle_p95-5_dist"])
    GENO = TAB.Genotype.unique()
    AR_AT = TAB.angle_at.unique()

    OUT_DIR = cfg["ANGLE_RANGE_OUTDIR"]

    for gen in GENO:
        for angle_at in AR_AT:
            tab_sub = TAB[(TAB.Genotype == gen) & (TAB.angle_at == angle_at)]
            if len(tab_sub) > 0:
                for feature in [
                    "angle_p95-5_dist",
                    "angle_std",
                ]:
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
                    ax.set_title(f"{gen} {angle_at}")
                    plt.savefig(
                        f"{OUT_DIR}/{gen}_{angle_at}_{feature}.pdf",
                        bbox_inches="tight",
                    )
                    plt.close(f)


if __name__ == "__main__":

    cfg = settings()

    plot_by_geno(cfg)
    plot_by_stage(cfg)
