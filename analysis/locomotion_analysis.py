import os
import pathlib


import numpy as np
import pandas as pd
import roifile
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import tadpose

from tqdm.auto import tqdm, trange

from shared import settings
from tadpose.utils import directional_change


def get_body_size(tad, parts, track_idx=0):
    px_size = tadpose.utils.calibrate_by_dish(tad, dish_diamter_in_cm=14)
    body_locs = tad.locs(parts=parts, track_idx=track_idx, fill_missing=False)

    body_size = np.linalg.norm(body_locs[:, 0] - body_locs[:, 1], axis=1) * px_size
    return np.nanmean(body_size)


def locomotion(tad, tids, stg, gen, cfg, write_imgs=True):
    cfgs = cfg[stg]
    file_path = tad.video_fn
    base_file = os.path.basename(file_path)[:-4]

    os.makedirs(f"{cfg['LOCOMOTION_OUTDIR']}/imgs/{stg}/{gen}", exist_ok=True)
    roi = roifile.roiread(file_path[:-4] + ".roi")

    x_a, x_b = roi.left, roi.right
    y_a, y_b = roi.top, roi.bottom

    roi_center = (x_a + (x_b - x_a) / 2, y_a + (y_b - y_a) / 2)
    roi_radius = (x_b - x_a) / 2

    frame_step = cfg["LOCOMOTION_PLOT_INTERVAL_MIN"] * 60 * cfg["FPS"]

    tab_res = []

    for tid in tids:
        if write_imgs:
            locs = tad.locs(track_idx=tid, parts=(cfgs["LOCOMOTION_NODE"],)).squeeze()
            for frame_start in range(0, tad.nframes, frame_step):
                t_start_min = int(frame_start / 60 / cfg["FPS"])
                f, ax = plt.subplots(figsize=(10, 10))
                ax.plot(*locs[frame_start : frame_start + frame_step].T, "r-")

                ax.add_patch(
                    Circle(roi_center, radius=roi_radius, color="k", fill=False)
                )

                ax.set_axis_off()
                ax.invert_yaxis()
                ax.set_title(
                    f"Trajectory of {cfgs['LOCOMOTION_NODE']}\n{os.path.basename(file_path)}, Tid: {tid} Time: {t_start_min} - {t_start_min + cfg['LOCOMOTION_PLOT_INTERVAL_MIN']} min"
                )

                plt.savefig(
                    f"{cfg['LOCOMOTION_OUTDIR']}/imgs/{stg}/{gen}/{base_file}_{tid}_{t_start_min:03d}min.png"
                )
                plt.close(f)

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

        time_spent_moving = moving_bin.sum() / tad.nframes

        # speed_mean = speed_calib.mean()
        # speed_std = speed_calib.std()

        total_dist = speed_calib[moving_bin].sum() / cfg["FPS"]

        acceleration = np.gradient(speed_calib)

        part_loc = tad.locs(parts=(cfgs["LOCOMOTION_NODE"],), track_idx=tid).squeeze()
        dc_angles = directional_change(
            part_loc,
            sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
            subsample=cfgs["LOCOMOTION_DC_SUBSAMPLE"],
        )

        moving_sub = moving_bin[:: cfgs["LOCOMOTION_DC_SUBSAMPLE"]][1:-1]

        body_size_parts = (cfgs["ALIGN_CENTRAL"], cfgs["ALIGN_TOP"])
        body_size_mean = get_body_size(tad, body_size_parts, tid)

        if np.any(moving_sub):
            dc_mov = dc_angles[moving_sub]
            dc_abs = np.abs(dc_mov)
            dc_pos = dc_mov[dc_mov > 0]
            dc_neg = np.abs(dc_mov[dc_mov < 0])

            if len(dc_abs) > 1:
                directional_change_mean = dc_abs.mean()
                directional_change_std = dc_abs.std()
                directional_change_95 = np.percentile(dc_abs, 95)
            else:
                directional_change_mean = np.nan
                directional_change_std = np.nan
                directional_change_95 = np.nan

            if len(dc_pos) > 1:
                directional_change_pos_mean = dc_pos.mean()
                directional_change_pos_std = dc_pos.std()
                directional_change_pos_95 = np.percentile(dc_pos, 95)
            else:
                directional_change_pos_mean = np.nan
                directional_change_pos_std = np.nan
                directional_change_pos_95 = np.nan

            if len(dc_neg) > 1:
                directional_change_neg_mean = dc_neg.mean()
                directional_change_neg_std = dc_neg.std()
                directional_change_neg_95 = np.percentile(dc_neg, 95)
            else:
                directional_change_neg_mean = np.nan
                directional_change_neg_std = np.nan
                directional_change_neg_95 = np.nan

        else:
            directional_change_mean = np.nan
            directional_change_std = np.nan
            directional_change_95 = np.nan

            directional_change_pos_mean = np.nan
            directional_change_pos_std = np.nan
            directional_change_pos_95 = np.nan

            directional_change_neg_mean = np.nan
            directional_change_neg_std = np.nan
            directional_change_neg_95 = np.nan

        speed_moving_mean = 0
        speed_moving_std = np.nan
        speed_moving_p95 = 0

        if time_spent_moving > 0:
            speed_moving_mean = speed_calib[moving_bin].mean()
            speed_moving_std = speed_calib[moving_bin].std()
            speed_moving_p95 = np.percentile(speed_calib[moving_bin], 95)

        tab_res.append(
            [
                base_file,
                tid,
                # speed_mean,
                # speed_std,
                speed_moving_mean,
                speed_moving_std,
                speed_moving_p95,
                time_spent_moving * 100,  # in percent
                directional_change_mean,
                directional_change_std,
                directional_change_95,
                directional_change_pos_mean,
                directional_change_pos_std,
                directional_change_pos_95,
                directional_change_neg_mean,
                directional_change_neg_std,
                directional_change_neg_95,
                acceleration[acceleration > 0].mean(),
                np.percentile(acceleration[acceleration > 0], 95),
                # acceleration[acceleration > 0].max(),
                total_dist,
                body_size_mean,
                speed_moving_mean / body_size_mean,
                speed_moving_std / body_size_mean,
                speed_moving_p95 / body_size_mean,
                acceleration[acceleration > 0].mean() / body_size_mean,
                np.percentile(acceleration[acceleration > 0], 95) / body_size_mean,
                total_dist / body_size_mean,
            ]
        )

    return pd.DataFrame(
        tab_res,
        columns=[
            "Movie",
            "track_idx",
            # "speed_mean",
            # "speed_std",
            "speed_moving_mean",
            "speed_moving_std",
            "speed_moving_p95",
            "time_spend_moving_ratio",
            "directional_change_mean",
            "directional_change_std",
            "directional_change_95",
            "directional_change_pos_mean",
            "directional_change_pos_std",
            "directional_change_pos_95",
            "directional_change_neg_mean",
            "directional_change_neg_std",
            "directional_change_neg_95",
            "acceleration_mean",
            "acceleration_p95",
            # "acceleration_max",
            "total_distance",
            # NEW
            "body_size_mean",
            "body_size_norm_speed_moving_mean",
            "body_size_norm_speed_moving_std",
            "body_size_norm_speed_moving_p95",
            "body_size_norm_acceleration_mean",
            "body_size_norm_acceleration_p95",
            "body_size_norm_total_distance",
        ],
    )


def run_stage(STAGE, cfg):
    cfgs = cfg[STAGE]
    ROOT_DIR = pathlib.Path(cfgs["ROOT_DIR"])

    all_movs = list(ROOT_DIR.rglob("*.mp4"))
    print(f" - Processing Stage {STAGE} with {len(all_movs)} movies")

    tab_stg = []
    for fn in tqdm(all_movs, desc=f"Locomotion"):
        gen = fn.parent.stem
        stg = fn.parent.parent.stem
        assert stg == STAGE, "Stage mismatch!!"

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

        tab_mov = locomotion(tad, track_okay_idx, stg, gen, cfg)
        tab_stg.append(tab_mov)

        tab_mov.insert(1, "Frames", tad.nframes)
        tab_mov.insert(1, "Genotype", gen)
        tab_mov.insert(1, "Stage", stg)

    tab_stg = pd.concat(tab_stg, axis=0, ignore_index=True)

    tab_stg.to_csv(f"{cfg['LOCOMOTION_OUTDIR']}/locomotion_{STAGE}_res.tab", sep="\t")
    return tab_stg


def run(STAGES, cfg):
    tab_all = []

    for STAGE in STAGES:
        tab_stg = run_stage(STAGE, cfg)
        tab_all.append(tab_stg)

    tab_all = pd.concat(tab_all, axis=0, ignore_index=True)
    tab_all.to_csv(f"{cfg['LOCOMOTION_OUTDIR']}/locomotion_res.tab", sep="\t")
    return tab_all


def main(cfg=None):
    if cfg is None:
        cfg = settings()
    os.makedirs(cfg["LOCOMOTION_OUTDIR"], exist_ok=True)

    STAGES = cfg["STAGES"]
    run(STAGES, cfg)


if __name__ == "__main__":
    main()
