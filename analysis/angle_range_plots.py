import numpy as np
import pandas as pd

import seaborn as sns
from matplotlib import pyplot as plt

from shared import settings


def plot_by_stage(cfg):
    OUT_DIR = cfg["ANGLE_RANGE_OUTDIR"]
    TAB = pd.read_csv(f"{OUT_DIR}/angle_range_res.tab", sep="\t", index_col=0)

    STAGES = cfg["STAGES"]

    AR_AT = TAB.angle_at.unique()

    OUT_DIR = cfg["ANGLE_RANGE_OUTDIR"]

    for stg in STAGES:
        for angle_at in AR_AT:
            tab_sub = TAB[(TAB.Stage == stg) & (TAB.angle_at == angle_at)]
            if len(tab_sub) > 0:
                for feature in [
                    "angle_moving_std",
                    "angle_moving_p05",
                    "angle_moving_mean",
                    "angle_moving_p95",
                    "angle_non-moving_std",
                    "angle_non-moving_p05",
                    "angle_non-moving_mean",
                    "angle_non-moving_p95",
                    "angular_speed_mov_pos_mean",
                    "angular_speed_mov_pos_std,",
                    "angular_speed_mov_pos_p95,",
                    "angular_speed_mov_neg_mean",
                    "angular_speed_mov_neg_std,",
                    "angular_speed_mov_neg_p95,",
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
    OUT_DIR = cfg["ANGLE_RANGE_OUTDIR"]
    TAB = pd.read_csv(f"{OUT_DIR}/angle_range_res.tab", sep="\t", index_col=0)

    GENO = TAB.Genotype.unique()
    AR_AT = TAB.angle_at.unique()

    OUT_DIR = cfg["ANGLE_RANGE_OUTDIR"]

    for gen in GENO:
        for angle_at in AR_AT:
            tab_sub = TAB[(TAB.Genotype == gen) & (TAB.angle_at == angle_at)]
            if len(tab_sub) > 0:
                for feature in [
                    "angle_moving_std",
                    "angle_moving_p05",
                    "angle_moving_mean",
                    "angle_moving_p95",
                    "angle_non-moving_std",
                    "angle_non-moving_p05",
                    "angle_non-moving_mean",
                    "angle_non-moving_p95",
                    "angular_speed_mov_pos_mean",
                    "angular_speed_mov_pos_std,",
                    "angular_speed_mov_pos_p95,",
                    "angular_speed_mov_neg_mean",
                    "angular_speed_mov_neg_std,",
                    "angular_speed_mov_neg_p95,",
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


def plot(cfg):
    plot_by_geno(cfg)
    plot_by_stage(cfg)


if __name__ == "__main__":
    cfg = settings()

    plot(cfg)
