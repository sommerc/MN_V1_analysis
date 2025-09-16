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

from matplotlib import cm
from matplotlib import colors
from matplotlib import colors as mpl_colors
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
from skimage import draw
from sklearn.decomposition import PCA
from tqdm.auto import tqdm, trange

from shared import settings


def moving_plots(tad, tids, stg, gen, cfg):
    cfgs = cfg[stg]
    os.makedirs(cfg["MOVING_OUTDIR"], exist_ok=True)
    os.makedirs(f"{cfg['MOVING_OUTDIR']}/{stg}/{gen}", exist_ok=True)

    file_path = tad.video_fn
    base_file = os.path.basename(file_path)[:-4]

    mov_result = []
    for tid in tids:
        speed_px_per_frame = tad.speed(
            cfgs["LOCOMOTION_NODE"], track_idx=tid, pre_sigma=60, sigma=30
        )
        speed_calib = (
            speed_px_per_frame
            * cfg["FPS"]
            * tadpose.utils.calibrate_by_dish(
                tad,
                dish_diamter_in_cm=14,
            )
        )

        moving_bin = speed_calib > cfgs["LOCOMOTION_MOVING_THRESH"]

        mov_result.append(moving_bin)

    mov_pd = np.stack(mov_result)

    if (mov_pd.shape[1] - cfg["MOVING_PLOT_TIME_SPAN_MIN"] * 60 * 60) > 0:
        start = np.random.randint(
            mov_pd.shape[1] - cfg["MOVING_PLOT_TIME_SPAN_MIN"] * 60 * 60
        )
        mov_pd = pd.DataFrame(
            mov_pd[:, start : start + 36000],
            index=[f"Animal {i + 1}" for i in range(len(tids))],
        )

        f, ax = plt.subplots(figsize=(8, len(tids) / 2))
        hm = sns.heatmap(mov_pd, cmap="gray_r", cbar=False, xticklabels=False, ax=ax)
        hm.set_yticklabels(hm.get_yticklabels(), rotation=0)

        ax.set_title(f"{base_file}")

        plt.savefig(
            f"{cfg['MOVING_OUTDIR']}/{stg}/{gen}/{base_file}_{cfg['MOVING_PLOT_TIME_SPAN_MIN']}min-random.png"
        )
        plt.close(f)


def pca_plot(tad, tids, stg, gen, cfg, pca_on):
    os.makedirs(cfg["PCA_OUTDIR"], exist_ok=True)
    os.makedirs(f"{cfg['PCA_OUTDIR']}/{stg}/{gen}", exist_ok=True)
    cfgs = cfg[stg]
    np.random.seed(42)

    file_path = tad.video_fn
    base_file = os.path.basename(file_path)[:-4]

    parts_dict = cfgs["PCA_PARTS"]
    size_pca = cfg["PCA_FIT_ON_N"]
    size_plot = cfg["PCA_PLOT_N"]

    for part_name, parts in parts_dict.items():
        norm = colors.Normalize(vmin=-5, vmax=5, clip=True)
        f, axs = plt.subplots(1, len(tids), squeeze=False, sharey=True)

        for i, tid in enumerate(tids):
            if pca_on in ["moving", "non-moving"]:
                speed_px_per_frame = tad.speed(
                    cfgs["LOCOMOTION_NODE"],
                    track_idx=tid,
                    pre_sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
                    sigma=cfgs["LOCOMOTION_TEMPORAL_SIGMA"],
                )
                speed_calib = (
                    speed_px_per_frame
                    * cfg["FPS"]
                    * tadpose.utils.calibrate_by_dish(
                        tad,
                        dish_diamter_in_cm=14,
                    )
                )

                moving_bin = speed_calib > cfgs["LOCOMOTION_MOVING_THRESH"]

                if pca_on.startswith("non"):
                    moving_bin = ~moving_bin

                try:
                    pca_sel = np.random.choice(
                        (moving_bin).nonzero()[0], size=size_pca, replace=False
                    )
                except ValueError:
                    print(
                        f"WARNING: PCA could not be done, since to few valid {pca_on} frames in {tad.video_fn} for tid {tid}"
                    )
                    continue

            elif pca_on == "all":
                pca_sel = np.random.randint(
                    tad.nframes,
                    size=size_pca,
                )

            else:
                raise RuntimeError(
                    f"PCA plots type {pca_on} not understood for file {tad.video_fn}"
                )

            part_locs = tad.ego_locs(parts=parts, track_idx=tid, fill_missing=True)[
                pca_sel
            ]

            X = part_locs.reshape(part_locs.shape[0], -1)

            # save for plotting
            X2plot = X.copy()

            # not constant locations
            X = X[:, X.std(0) != 0]

            # center and make unit variance
            Xc = (X - X.mean(0)) / X.std(0)

            if np.any(np.isnan(Xc)):
                # try to remove nan cols
                nan_frames = np.any(np.isnan(Xc), axis=1)
                if nan_frames.sum() < size_pca // 2:
                    print(
                        f"WARNING: NaN occured for {pca_on} frames in {tad.video_fn} for tid {tid}... trying to remove them and do PCA on fewer frames"
                    )
                    Xc = Xc[~nan_frames, :]
                    X2plot = X2plot[~nan_frames, :]

                else:
                    axs[0, i].set_axis_off()
                    print(
                        f"WARNING: PCA could not be done, NaN occured for {pca_on} frames in {tad.video_fn} for tid {tid}"
                    )
                    continue

            # Xp will contain the PCA components
            pca = PCA(n_components=1)
            pca.fit(Xc)
            Xpca = pca.transform(Xc)

            pc = 0

            for rand_ind in np.random.randint(X2plot.shape[0], size=size_plot):
                points = X2plot[rand_ind, :]
                load = Xpca[rand_ind, pc]
                color = cm.seismic(norm(load))
                p = axs[0, i].plot(
                    -points[::2].T, points[1::2].T, ".-", alpha=0.2, color=color
                )
                axs[0, i].set_aspect(1.0)
                axs[0, i].set_axis_off()

        f.suptitle(f"PCA skeletons ({pca_on})\n{stg} {gen} {part_name} {base_file}")

        sm = plt.cm.ScalarMappable(cmap="seismic", norm=norm)
        cbar = plt.colorbar(
            sm,
            # fraction=0.033,
            pad=0.1,
            ax=axs[0, -1],
        )
        cbar.ax.set_ylabel("PC 0")
        plt.tight_layout()
        plt.savefig(
            f"{cfg['PCA_OUTDIR']}/{stg}/{gen}/{part_name}_{base_file}_{pca_on}.pdf"
        )
        plt.close()


def run_stage(STAGE, cfg):
    cfgs = cfg[STAGE]
    ROOT_DIR = pathlib.Path(cfgs["ROOT_DIR"])

    all_movs = list(ROOT_DIR.rglob("*.mp4"))
    print(f" - Processing Stage {STAGE} with {len(all_movs)} movies")

    for fn in tqdm(all_movs, desc=f"PCA + Moving plots"):
        gen = fn.parent.stem
        stg = fn.parent.parent.stem

        tad = tadpose.Tadpole.from_sleap(str(fn))
        track_okay_idx = np.nonzero(
            np.atleast_1d(
                tad.parts_detected(
                    parts=(cfgs["LOCOMOTION_NODE"],), track_idx=None
                ).sum(0)
                / tad.nframes
                > cfgs["TRACK_SELECT_THRES"]
            )
        )[0]

        if len(track_okay_idx) > 0:
            moving_plots(tad, track_okay_idx, stg, gen, cfg)

            aligner = tadpose.alignment.RotationalAligner(
                central_part=cfgs["ALIGN_CENTRAL"], aligned_part=cfgs["ALIGN_TOP"]
            )
            aligner.tracks_to_align = track_okay_idx

            tad.aligner = aligner
            pca_plot(tad, track_okay_idx, stg, gen, cfg, "moving")
            pca_plot(tad, track_okay_idx, stg, gen, cfg, "non-moving")
            pca_plot(tad, track_okay_idx, stg, gen, cfg, "all")


def run(STAGES, cfg):
    for STAGE in STAGES:
        run_stage(STAGE, cfg)


def main(cfg=None):
    if cfg is None:
        cfg = settings()

    STAGES = cfg["STAGES"]
    run(STAGES, cfg)


if __name__ == "__main__":
    main()
