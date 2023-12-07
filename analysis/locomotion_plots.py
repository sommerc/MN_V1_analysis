import os
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import colors as mpl_colors
from scipy.ndimage import gaussian_filter1d
from tqdm.auto import tqdm, trange

from shared import settings


def plot_by_stage(cfg):
    STAGES = cfg["STAGES"]
    OUT_DIR = cfg["LOCOMOTION_OUTDIR"]

    for STAGE in STAGES:
        tab_stg = pd.read_csv(
            f"{cfg['LOCOMOTION_OUTDIR']}/locomotion_{STAGE}_res.tab", sep="\t"
        )

        os.makedirs(OUT_DIR, exist_ok=True)

        for feature in [
            "speed_mean",
            "speed_std",
            "speed_moving_mean",
            "time_spend_moving",
            "directional_change_mean",
            "directional_change_std",
            "directional_change_95",
            "directional_change_pos_mean",
            "directional_change_pos_std",
            "directional_change_pos_95",
            "directional_change_neg_mean",
            "directional_change_neg_std",
            "directional_change_neg_95",
            "acceleration_p95",
            "acceleration_mean",
            "acceleration_max",
        ]:
            f, ax = plt.subplots(figsize=(14, 4))
            a = sns.boxenplot(
                y=feature,
                x="Genotype",
                data=tab_stg,
                ax=ax,
                hue="Genotype",
                box_kws={"alpha": 0.4},
                dodge=False,
            )
            # a.legend_.remove()
            b = sns.stripplot(
                y=feature,
                x="Genotype",
                data=tab_stg,
                ax=ax,
                hue="Genotype",
                dodge=False,
                zorder=1,
                legend=False,
            )
            sns.despine(ax=ax)
            ax.set_title(f"{STAGE} {feature}")
            plt.savefig(f"{OUT_DIR}/{STAGE}_{feature}.pdf", bbox_inches="tight")
            plt.close(f)

        count_tab = tab_stg.groupby("Genotype")[["track_idx"]].count().reset_index()

        f, ax = plt.subplots(figsize=(14, 4))
        sns.barplot(
            y="track_idx",
            x="Genotype",
            data=count_tab,
            hue="Genotype",
            dodge=False,
            ax=ax,
        )
        sns.despine(ax=ax)

        ax.set_title(f"{STAGE} Animal Counts")
        plt.savefig(f"{OUT_DIR}/{STAGE}_animal_counts.pdf", bbox_inches="tight")
        plt.close(f)

        time_tab = (
            tab_stg.groupby("Genotype")[["track_idx", "Frames"]]
            .sum("Frames")
            .reset_index()
        )
        time_tab["Hours"] = time_tab["Frames"] / (60 * 60 * 60)

        f, ax = plt.subplots(figsize=(14, 4))
        sns.barplot(
            y="Hours",
            x="Genotype",
            data=time_tab,
            hue="Genotype",
            dodge=False,
            ax=ax,
        )
        sns.despine(ax=ax)

        ax.set_title(f"{STAGE} Animal hours")
        plt.savefig(f"{OUT_DIR}/{STAGE}_animal_hours.pdf", bbox_inches="tight")
        plt.close(f)


def plot_by_geno(cfg):
    OUT_DIR = cfg["LOCOMOTION_OUTDIR"]
    TAB = pd.read_csv(f"{OUT_DIR}/locomotion_res.tab", sep="\t", index_col=0)

    GENO = TAB.Genotype.unique()

    OUT_DIR = cfg["LOCOMOTION_OUTDIR"]

    for gen in GENO:
        tab_sub = TAB[(TAB.Genotype == gen)]
        for feature in [
            "speed_mean",
            "speed_std",
            "speed_moving_mean",
            "time_spend_moving",
            "directional_change_mean",
            "directional_change_std",
            "directional_change_95",
            "directional_change_pos_mean",
            "directional_change_pos_std",
            "directional_change_pos_95",
            "directional_change_neg_mean",
            "directional_change_neg_std",
            "directional_change_neg_95",
            "acceleration_p95",
            "acceleration_mean",
            "acceleration_max",
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
            # a.legend_.remove()
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

        count_tab = tab_sub.groupby("Stage")[["track_idx"]].count().reset_index()

        f, ax = plt.subplots(figsize=(14, 4))
        sns.barplot(
            y="track_idx",
            x="Stage",
            data=count_tab,
            dodge=False,
            hue="Stage",
            ax=ax,
        )
        sns.despine(ax=ax)

        ax.set_title(f"{gen} Animal Counts")
        plt.savefig(f"{OUT_DIR}/{gen}_animal_counts.pdf", bbox_inches="tight")
        plt.close(f)

        time_tab = (
            tab_sub.groupby("Stage")[["track_idx", "Frames"]]
            .sum("Frames")
            .reset_index()
        )
        time_tab["Hours"] = time_tab["Frames"] / (60 * 60 * 60)

        f, ax = plt.subplots(figsize=(14, 4))
        sns.barplot(
            y="Hours",
            x="Stage",
            data=time_tab,
            dodge=False,
            hue="Stage",
            ax=ax,
        )
        sns.despine(ax=ax)

        ax.set_title(f"{gen} Animal hours")
        plt.savefig(f"{OUT_DIR}/{gen}_animal_hours.pdf", bbox_inches="tight")
        plt.close(f)


def plot(cfg):
    plot_by_geno(cfg)
    plot_by_stage(cfg)


if __name__ == "__main__":
    cfg = settings()

    plot(cfg)
