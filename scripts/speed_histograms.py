import os
import sys
import pathlib
import tadpose
import numpy as np
import seaborn as sns

from matplotlib import pyplot as plt
from collections import defaultdict

sys.path.append("..")
from analysis.shared import settings

if __name__ == "__main__":
    # Collect all WT movies
    cfg = settings()

    wt_movs = {}
    for stg in cfg["STAGES"]:
        stg_root = pathlib.Path(cfg[stg]["ROOT_DIR"])
        wt_movs[stg] = list(map(str, list((stg_root / "WT").glob("*.mp4"))))

    # Extradct callibratet speed
    def get_calibrated_speed(tad, cfgs, dish_size):
        speed_px_per_frame = tad.speed(
            cfgs["LOCOMOTION_NODE"],
            track_idx=tid,
            pre_sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
            sigma=cfgs["LOCOMOTION_TEMPORAL_SIGMA"],
        )
        speed_calib = speed_px_per_frame * tadpose.utils.calibrate_by_dish(
            tad, dish_size
        )

        return speed_calib

    stg_speeds = defaultdict(list)

    for stg, movs in wt_movs.items():
        cfgs = cfg[stg]
        print(" * Get WT speeds for:", stg)
        for mov in movs:
            tad = tadpose.Tadpole.from_sleap(mov)
            tid = 0
            speed_calib = get_calibrated_speed(tad, cfgs, 14)

            stg_speeds[stg].append(speed_calib)

    # Make histogram and plots

    out_dir = "speed_hists"

    os.makedirs(out_dir, exist_ok=True)

    for stg, speeds in stg_speeds.items():
        if stg == "37-38":
            continue
        hist, stg_bins = np.histogram(
            np.concatenate(speeds), bins=128, range=[0, 0.16], density=True
        )

        f, ax = plt.subplots()
        ax.bar(stg_bins[:-1], hist, width=0.16 / 128)
        ax.vlines(0.02, ymin=0, ymax=128, color="r", label="Moving Threshold")
        ax.set_xlabel("Speed (cm/frame)")
        ax.set_ylabel("Count (density)")
        ax.set_title(f"Stage: {stg}")
        ax.legend()
        sns.despine(ax=ax)
        plt.savefig(f"{out_dir}{stg}.png")

        stg = "37-38"
        hist, stg_bins = np.histogram(
            np.concatenate(stg_speeds[stg]), bins=128, range=[0, 0.0005], density=True
        )

        f, ax = plt.subplots()
        ax.bar(stg_bins[:-1], hist, width=0.0005 / 128)
        ax.vlines(
            0.0002,
            ymin=0,
            ymax=10000,
            color="r",
            label=f"Moving Threshold Stage: {stg}",
        )
        ax.set_xlabel("Speed (cm/frame)")
        ax.set_ylabel("Count (density)")
        ax.set_title(f"Stage: {stg}")
        ax.legend()
        ax.set_ylim(0, 20000)
        sns.despine(ax=ax)
        plt.tight_layout()
        plt.savefig(f"{out_dir}{stg}.png")
