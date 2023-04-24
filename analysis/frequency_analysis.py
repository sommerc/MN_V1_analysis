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
from scipy.ndimage import gaussian_filter1d

import pywt
from scipy import signal

from shared import settings


def compute_angle_wavlet_psd_mean(
    tad, tid, scales, wavelet, a, b, c, fps, sub_bgrd, cfgs
):
    ang = tadpose.analysis.angles(tad, (a, b), (b, c), win=None, track_idx=tid)
    ang_smooth = gaussian_filter1d(ang, cfgs["FREQ_TEMP_ANGLE_SMOOTH"])

    if sub_bgrd:
        ang_background = gaussian_filter1d(ang, cfgs["FREQ_ACTIVE_SMOOTH"])
    else:
        ang_background = 0

    ang_smooth -= ang_background

    ang_zscore = (ang_smooth - ang_smooth.mean()) / ang_smooth.std()

    t_wvlt, freq = pywt.cwt(
        ang_zscore,
        scales,
        wavelet,
        sampling_period=1 / fps,
        method="fft",
    )
    t_wvlt_psd = np.abs(t_wvlt.T) ** 2

    # speed_px_per_frame = tad.speed(
    #     cfgs["FREQ_MOVING_NODE"],
    #     track_idx=tid,
    #     pre_sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
    #     sigma=cfgs["LOCOMOTION_TEMPORAL_SIGMA"],
    # )
    # speed_calib = speed_px_per_frame * tadpose.utils.calibrate_by_dish(tad, 14)

    # moving_bin = speed_calib > cfgs["FREQ_MOVING_NODE_THRESH"]

    ang_grad_mag = gaussian_filter1d(
        np.abs(np.gradient(ang_zscore)), cfgs["FREQ_ACTIVE_SMOOTH"]
    )

    moving_bin = ang_grad_mag > cfgs["FREQ_ACTIVE_THRESH"]

    computed_on = moving_bin.sum() / tad.nframes

    mean_psd_moving = t_wvlt_psd[moving_bin].mean(0)

    return mean_psd_moving, freq, computed_on


def dominant_freqency(sig, freq):
    peaks, props = signal.find_peaks(sig, height=(None, None), prominence=(None, None))

    if len(peaks) > 0:
        peak_pos = np.argmax(props["peak_heights"])
        dom_f = freq[peaks[peak_pos]]
        dom_p = props["prominences"][peak_pos]
        return dom_f, dom_p
    return None, None


def get_frequency_params(cfg):
    N = cfg["FREQUENCY_N"]
    wavelet = cfg["FREQUENCY_WAVELET"]

    # Fc = pywt.central_frequency(wavelet)
    fps = cfg["FPS"]
    sp = 1 / fps

    scales = 2 ** np.linspace(1, 6, N)  # <- dyadic 1-30HZ
    frequencies = pywt.scale2frequency(wavelet, scales) / sp
    return scales, frequencies, wavelet, fps


def frequency_analysis(all_movs, stg, nodes, sub_bgrd, cfg):
    cfgs = cfg[stg]
    scales, freq, wavelet, fps = get_frequency_params(cfg)
    tab_all = []
    for fn in tqdm(all_movs, desc=f"Frequency {nodes[1]}"):
        gen = fn.parent.stem
        stg = fn.parent.parent.stem

        tail_a, tail_b, tail_c = nodes

        tad = tadpose.Tadpole.from_sleap(str(fn))
        track_okay_idx = np.nonzero(
            tad.parts_detected(parts=(tail_b,), track_idx=None).sum(0) / tad.nframes
            > cfgs["TRACK_SELECT_THRES"]
        )[0]

        file_path = tad.video_fn
        base_file = os.path.basename(file_path)[:-4]

        for tid in track_okay_idx:
            mean_psd_moving, freq, computed_on = compute_angle_wavlet_psd_mean(
                tad, tid, scales, wavelet, tail_a, tail_b, tail_c, fps, sub_bgrd, cfgs
            )

            dom_freq, dom_prom = dominant_freqency(mean_psd_moving, freq)

            tab_all.append(
                [
                    base_file,
                    stg,
                    gen,
                    tid,
                    dom_freq,
                    dom_prom,
                    computed_on,
                ]
                + mean_psd_moving.tolist()
            )

    tab_freq = pd.DataFrame(
        tab_all,
        columns=[
            "Movie",
            "Stage",
            "Genotype",
            "Track_idx",
            "dominant_freq",
            "dominant_freq_prominence",
            "freq_active_ratio",
        ]
        + freq.tolist(),
    )

    return tab_freq


def run_stage(STAGE, cfg):
    cfgs = cfg[STAGE]
    ROOT_DIR = pathlib.Path(cfgs["ROOT_DIR"])

    all_movs = list(ROOT_DIR.rglob("*.mp4"))
    print(f" - Processing Stage {STAGE} with {len(all_movs)} movies")

    tab_freq_dict = {}
    if "FREQ_FOR" in cfgs:
        for name, nodes in cfgs["FREQ_FOR"].items():
            # Without background sub

            out_f1 = f"{cfg['FREQUENCY_OUTDIR']}/frequency_{STAGE}_{name}_res.tab"
            if not os.path.exists(out_f1):
                tab_freq = frequency_analysis(all_movs, STAGE, nodes, False, cfg)

                tab_freq.to_csv(out_f1, sep="\t")
            else:
                tab_freq = pd.read_csv(out_f1, sep="\t", index_col=0)

            tab_freq_dict[name] = tab_freq

            # With
            out_f2 = f"{cfg['FREQUENCY_OUTDIR']}/frequency_bs_{STAGE}_{name}_res.tab"
            if not os.path.exists(out_f2):
                tab_freq = frequency_analysis(all_movs, STAGE, nodes, True, cfg)

                tab_freq.to_csv(
                    out_f2,
                    sep="\t",
                )
            else:
                tab_freq = pd.read_csv(out_f2, sep="\t", index_col=0)

            tab_freq_dict["bs_" + name] = tab_freq

    else:
        print("  -- no FREQ_FOR set")

    return tab_freq_dict


def run(STAGES, cfg):
    tab_dict_all = []

    for STAGE in STAGES:
        tab_dict_stg = run_stage(STAGE, cfg)
        tab_dict_all.append(tab_dict_stg)

    tab_collect = []
    for tab_dict in tab_dict_all:
        for name, tab in tab_dict.items():
            tab["frequency_for"] = name
            tab_collect.append(tab)

    if len(tab_collect) == 0:
        return

    tab_collect = pd.concat(tab_collect, axis=0, ignore_index=True)
    tab_collect.to_csv(f"{cfg['FREQUENCY_OUTDIR']}/frequency_res.tab", sep="\t")
    return tab_collect


def main(cfg=None):
    if cfg is None:
        cfg = settings()
    os.makedirs(cfg["FREQUENCY_OUTDIR"], exist_ok=True)

    STAGES = cfg["STAGES"]
    run(STAGES, cfg)


if __name__ == "__main__":
    main()
