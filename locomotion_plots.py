import os
import pathlib
from collections import defaultdict

import cv2
import yaml
import h5py
import numpy as np
import pandas as pd
import roifile
import seaborn as sns
import tadpose
from matplotlib import pyplot as plt
from matplotlib import colors as mpl_colors
from scipy.ndimage import gaussian_filter1d
from skimage import draw
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
            # "directional_change_95"
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
            a.legend_.remove()
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
