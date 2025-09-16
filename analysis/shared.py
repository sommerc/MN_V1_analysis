import os
import shutil
import yaml
import pathlib

import numpy as np
from scipy.ndimage import gaussian_filter1d


def settings(config_yml=None):
    if config_yml is None:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.wm_attributes("-topmost", 1)
        root.withdraw()

        config_yml = filedialog.askopenfilename(
            parent=root,
            title="Choose analysis settings YAML",
            defaultextension=".yml",
            filetypes=[("YAML file", ".yml .yaml")],
        )

        if len(config_yml) == 0:
            raise RuntimeError(f"YAML file '{config_yml}' does not exist... abort")

        # config_yml = "H:/projects/068_lora_tadpole/paper_code/analysis_settings.yml"

    print(f" - Using settings '{config_yml}'")

    with open(config_yml, "r") as ymlfile:
        config_dict = yaml.safe_load(ymlfile)

    for key in config_dict.keys():
        result_root = config_dict["RESULTS_ROOT_DIR"]
        if key.endswith("_OUTDIR"):
            config_dict[key] = os.path.join(result_root, config_dict[key])

    os.makedirs(config_dict["RESULTS_ROOT_DIR"], exist_ok=True)
    print(f" - Results -> '{config_dict['RESULTS_ROOT_DIR']}'")

    shutil.copy(config_yml, f"{config_dict['RESULTS_ROOT_DIR']}/used_settings.yaml")

    return config_dict


import matplotlib.pyplot as plt
import numpy as np
import tadpose
import yaml

from matplotlib import colors

from matplotlib import pyplot as plt
from sklearn.decomposition import PCA


def set_frog(fn, cfgs):
    gen = fn.parent.stem
    stg = fn.parent.parent.stem

    print(f"Reading {fn}")

    tad = tadpose.Tadpole.from_sleap(str(fn))
    print(f" - Checking tracks")
    track_okay_idx = np.nonzero(
        np.atleast_1d(
            tad.parts_detected(parts=(cfgs["LOCOMOTION_NODE"],), track_idx=None).sum(0)
            / tad.nframes
            > cfgs["TRACK_SELECT_THRES"]
        )
    )[0]

    if len(track_okay_idx) == 0:
        raise RuntimeError(f"No valid tracks found in {fn}")

    aligner = tadpose.alignment.RotationalAligner(
        central_part=cfgs["ALIGN_CENTRAL"], aligned_part=cfgs["ALIGN_TOP"]
    )

    aligner.tracks_to_align = track_okay_idx

    print(f" - Aligning")
    tad.aligner = aligner
    print(f"Done")
    return tad


def show_pca(
    cfgs,
    tad,
    parts_dict,
    size_pca,
    size_plot,
    cmap_line,
    cmap_dots,
    vmin=-5,
    vmax=5,
    alpha_line=0.2,
    alpha_dots=0.2,
    figsize=(20, 8),
    line_zorder=99,
    pca_for=("all", "moving", "non-moving"),
    save_pdf=True,
):
    np.random.seed(42)

    file_path = tad.video_fn
    base_file = os.path.basename(file_path)[:-4]

    gen = pathlib.Path(file_path).parent.stem

    for part_name, parts in parts_dict.items():
        f, axs = plt.subplots(
            len(tad.aligner.tracks_to_align),
            len(pca_for),
            squeeze=False,
            sharey=True,
            sharex=True,
            figsize=figsize,
        )

        for i, tid in enumerate(tad.aligner.tracks_to_align):
            for p_i, pca_on in enumerate(pca_for):
                if pca_on in ["moving", "non-moving"]:
                    speed_px_per_frame = tad.speed(
                        cfgs["LOCOMOTION_NODE"],
                        track_idx=tid,
                        pre_sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
                        sigma=cfgs["LOCOMOTION_TEMPORAL_SIGMA"],
                    )
                    speed_calib = (
                        60
                        * speed_px_per_frame
                        * tadpose.utils.calibrate_by_dish(tad, 14)
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
                        axs[i, 0].set_axis_off()
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

                    if cmap_line is not None:
                        norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
                        color = cmap_line(norm(load))

                        p = axs[i, p_i].plot(
                            -points[::2].T,
                            points[1::2].T,
                            "-",
                            alpha=alpha_line,
                            color=color,
                            zorder=line_zorder,
                        )

                    if cmap_dots is not None:
                        only_use = [
                            k
                            for (k, col) in enumerate(cmap_dots.colors)
                            if (col != "#00000000") and k < points[1::2].T.shape[0]
                        ]

                        p = axs[i, p_i].scatter(
                            -points[::2].T[only_use],
                            points[1::2].T[only_use],
                            alpha=alpha_dots,
                            c=cmap_dots._lut[: len(points[::2])][only_use],
                        )

                    axs[i, p_i].set_aspect(1.0)
                    axs[i, p_i].set_axis_off()

                axs[0, p_i].set_title(pca_on)

            f.suptitle(f"PCA skeletons {gen} {part_name} {base_file}")

            if cmap_line is not None:
                sm = plt.cm.ScalarMappable(cmap=cmap_line, norm=norm)
                cbar = plt.colorbar(
                    sm,
                    # fraction=0.033,
                    pad=0.1,
                    ax=axs[0, p_i],
                )
                cbar.ax.set_ylabel("PC 0")
            plt.tight_layout()
            if save_pdf:
                plt.savefig(f"{base_file}_{part_name}.pdf")
