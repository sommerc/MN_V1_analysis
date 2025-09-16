import os
import pathlib
from collections import defaultdict

import cv2
import h5py
import yaml
import numpy as np
import pandas as pd
import roifile
import seaborn as sns
import tadpose
from matplotlib import pyplot as plt
from matplotlib import colors as mpl_colors
from skimage import draw
from tqdm.auto import tqdm, trange

from shared import settings


def area_explored(tad, tids, cfg, stg, gen, write_img=False):
    cfgs = cfg[stg]
    area_bins = cfgs["AREA_EXPLORED_BINS"]

    hist_total = np.zeros((area_bins, area_bins))

    os.makedirs(f"{cfg['AREA_EXPLORED_OUTDIR']}/imgs/{stg}/{gen}", exist_ok=True)

    file_path = tad.video_fn
    base_file = os.path.basename(file_path)[:-4]

    # vid = cv2.VideoCapture(tad.video_fn)
    # height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    # vid.release()

    bins = area_bins

    mask_circ = draw.disk(
        (area_bins // 2, area_bins // 2),
        area_bins // 2,
        shape=(area_bins, area_bins),
    )
    mask = np.zeros((area_bins, area_bins), dtype=bool)
    mask[mask_circ] = True

    mask_area = mask.sum()

    tab_res = []

    for tid in tids:
        x_loc, y_loc = (
            tad.locs(parts=(cfgs["AREA_EXPLORED_NODE"],), track_idx=tid).squeeze().T
        )

        roi = roifile.roiread(file_path[:-4] + ".roi")

        x_a, x_b = roi.left, roi.right
        y_a, y_b = roi.top, roi.bottom

        coords = roi.coordinates()

        if "mutant_side" in tad.info and tad.info["mutant_side"] == "right":
            cap = cv2.VideoCapture(tad.video_fn)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            cap.release()

            x_a = width - roi.right
            x_b = width - roi.left

            coords[:, 0] = width - coords[:, 0]

        hist = np.histogram2d(y_loc, x_loc, bins=bins, range=[(y_a, y_b), (x_a, x_b)])[
            0
        ]

        area_expl = (hist > 0).sum()
        area_expl_ratio = area_expl / mask_area
        area_expl_rattio_per_h = area_expl_ratio * (216000 / tad.nframes)

        tab_res.append([base_file, tid, area_expl_ratio, area_expl_rattio_per_h])
        hist[~mask] = np.nan
        hist_total += hist

        ##########################################
        if write_img:
            img = tad.image(0)

            f, ax = plt.subplots(figsize=(10, 10))
            ax.imshow(img, "gray")
            ax.plot(*coords.T, "y.-")

            ax.imshow(
                np.log(hist + 1), alpha=0.3, extent=[x_a, x_b, y_b, y_a], cmap="hot"
            )

            ax.set_axis_off()
            ax.set_title(f"{os.path.basename(file_path)}, Tid: {tid}")

            plt.savefig(
                f"{cfg['AREA_EXPLORED_OUTDIR']}/imgs/{stg}/{gen}/{base_file}_{tid}.png"
            )
            plt.close(f)

    if len(tids) > 0 and write_img:
        vmax = max(10, np.nanmax(hist_total))
        f, ax = plt.subplots(figsize=(14, 10))
        im = ax.imshow(
            hist_total + 1, cmap="viridis_r", norm=mpl_colors.LogNorm(vmin=1, vmax=vmax)
        )
        ax.set_axis_off()
        ax.set_title(f"{os.path.basename(file_path)}")
        plt.colorbar(im, extend="max")
        plt.savefig(
            f"{cfg['AREA_EXPLORED_OUTDIR']}/imgs/{stg}/{gen}/{base_file}_all.png"
        )
        plt.close(f)

    return pd.DataFrame(
        tab_res,
        columns=["Movie", "track_idx", "area_explored_ratio", "area_explored_per_h"],
    )


def run_stage(STAGE, cfg):
    cfgs = cfg[STAGE]
    ROOT_DIR = pathlib.Path(cfgs["ROOT_DIR"])

    all_movs = list(ROOT_DIR.rglob("*.mp4"))
    print(f" - Processing Stage {STAGE} with {len(all_movs)} movies")

    tab_stg = []
    for fn in tqdm(all_movs, desc=f"Area explored"):
        gen = fn.parent.stem
        stg = fn.parent.parent.stem

        tad = tadpose.Tadpole.from_sleap(str(fn))
        track_okay_idx = np.nonzero(
            np.atleast_1d(
                tad.parts_detected(
                    parts=(cfgs["AREA_EXPLORED_NODE"],), track_idx=None
                ).sum(0)
                / tad.nframes
                > cfgs["TRACK_SELECT_THRES"]
            )
        )[0]

        tab_mov = area_explored(tad, track_okay_idx, cfg, stg, gen, write_img=True)
        tab_mov.insert(1, "Genotype", gen)
        tab_mov.insert(1, "Stage", stg)

        tab_stg.append(tab_mov)

    tab_stg = pd.concat(tab_stg, axis=0, ignore_index=True)

    tab_stg.to_csv(
        f"{cfg['AREA_EXPLORED_OUTDIR']}/area_explored_{STAGE}_res.tab", sep="\t"
    )

    return tab_stg


def run(STAGES, cfg):
    tab_all = []

    for STAGE in STAGES:
        tab_stg = run_stage(STAGE, cfg)
        tab_all.append(tab_stg)

    tab_all = pd.concat(tab_all, axis=0, ignore_index=True)
    tab_all.to_csv(f"{cfg['AREA_EXPLORED_OUTDIR']}/area_explored_res.tab", sep="\t")
    return tab_stg


def main(cfg=None):
    if cfg is None:
        cfg = settings()
    os.makedirs(cfg["AREA_EXPLORED_OUTDIR"], exist_ok=True)
    os.makedirs(f"{cfg['AREA_EXPLORED_OUTDIR']}/imgs", exist_ok=True)

    STAGES = cfg["STAGES"]
    run(STAGES, cfg)


if __name__ == "__main__":
    main()
