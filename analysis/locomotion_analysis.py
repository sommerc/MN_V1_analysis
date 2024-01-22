import os
import pathlib


import numpy as np
import pandas as pd

import tadpose

from tqdm.auto import tqdm, trange

from shared import settings, directional_change


def locomotion(tad, tids, cfgs):
    file_path = tad.video_fn
    base_file = os.path.basename(file_path)[:-4]

    tab_res = []

    for tid in tids:
        speed_px_per_frame = tad.speed(
            cfgs["LOCOMOTION_NODE"],
            track_idx=tid,
            pre_sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
            sigma=cfgs["LOCOMOTION_TEMPORAL_SIGMA"],
        )
        speed_calib = speed_px_per_frame * tadpose.utils.calibrate_by_dish(tad, 14)

        moving_bin = speed_calib > cfgs["LOCOMOTION_MOVING_THRESH"]

        time_spent_moving = moving_bin.sum() / tad.nframes

        speed_mean = speed_calib.mean()
        speed_std = speed_calib.std()
        total_dist = speed_calib.sum()

        acceleration = np.gradient(speed_calib)

        part_loc = tad.locs(parts=(cfgs["LOCOMOTION_NODE"],), track_idx=tid).squeeze()
        dc_angles = directional_change(
            part_loc,
            sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
            subsample=cfgs["LOCOMOTION_DC_SUBSAMPLE"],
        )

        moving_sub = moving_bin[:: cfgs["LOCOMOTION_DC_SUBSAMPLE"]][1:-1]

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
                speed_mean,
                speed_std,
                speed_moving_mean,
                speed_moving_std,
                speed_moving_p95,
                time_spent_moving,
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
                acceleration[acceleration > 0].max(),
                total_dist,
            ]
        )

    return pd.DataFrame(
        tab_res,
        columns=[
            "Movie",
            "track_idx",
            "speed_mean",
            "speed_std",
            "speed_moving_mean",
            "speed_moving_std",
            "speed_moving_p95",
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
            "acceleration_mean",
            "acceleration_p95",
            "acceleration_max",
            "total_distance",
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
            tad.parts_detected(parts=(cfgs["LOCOMOTION_NODE"],), track_idx=None).sum(0)
            / tad.nframes
            > cfgs["TRACK_SELECT_THRES"]
        )[0]

        tab_mov = locomotion(tad, track_okay_idx, cfgs)
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
