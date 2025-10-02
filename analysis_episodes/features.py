import numpy as np
from scipy.stats import skew
import tadpose
from scipy.ndimage import gaussian_filter1d
import pywt

from scipy import signal


def angle_range_episode(tad, episode, name, nodes_tuple, cfg):
    cfgs = cfg[episode.stage]
    frames = (episode.episode_start, episode.episode_stop)

    tail_a, tail_b, tail_c = nodes_tuple

    ang = tadpose.analysis.angles(
        tad,
        (tail_a, tail_b),
        (tail_b, tail_c),
        track_idx=episode.track_idx,
        frames=frames,
    )
    ang_smooth = gaussian_filter1d(ang, cfgs["FREQ_TEMP_ANGLE_SMOOTH"])

    speed_px_per_frame = tad.speed(
        cfgs["ANGLE_RANGE_MOVING_NODE"],
        track_idx=episode.track_idx,
        pre_sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
        sigma=cfgs["LOCOMOTION_TEMPORAL_SIGMA"],
        frames=frames,
    )
    speed_calib = (
        speed_px_per_frame
        * cfg["FPS"]
        * tadpose.utils.calibrate_by_dish(
            tad,
            dish_diamter_in_cm=14,
        )
    )

    moving_bin = speed_calib > cfgs["ANGLE_RANGE_MOVING_NODE_THRESH"]

    episode["name"] = name

    for c in [
        "angle_moving_std",
        "angle_moving_p05",
        "angle_moving_mean",
        "angle_moving_p95",
        "angle_non-moving_std",
        "angle_non-moving_p05",
        "angle_non-moving_mean",
        "angle_non-moving_p95",
        "angular_speed_mov_pos_mean",
        "angular_speed_mov_pos_std",
        "angular_speed_mov_pos_p95",
        "angular_speed_mov_neg_mean",
        "angular_speed_mov_neg_std",
        "angular_speed_mov_neg_p95",
    ]:
        episode[c] = None

    if moving_bin.sum() > 0:
        ang_std_mov = ang_smooth[moving_bin].std()
        ang_p05_mov, ang_p95_mov = np.percentile(ang_smooth[moving_bin], (5, 95))
        ang_mean_mov = ang_smooth[moving_bin].mean()

        episode["angle_moving_std"] = ang_std_mov
        episode["angle_moving_p05"] = ang_p05_mov
        episode["angle_moving_mean"] = ang_mean_mov
        episode["angle_moving_p95"] = ang_p95_mov

        ang_speeds = np.gradient(ang_smooth)

        if (ang_speeds > 0).sum() > 1:
            ang_mov_speed_pos_mean = ang_speeds[ang_speeds > 0].mean()
            ang_mov_speed_pos_std = ang_speeds[ang_speeds > 0].std()
            ang_mov_speed_pos_p95 = np.percentile(ang_speeds[ang_speeds > 0], 95)

            episode["angular_speed_mov_pos_mean"] = ang_mov_speed_pos_mean
            episode["angular_speed_mov_pos_std"] = ang_mov_speed_pos_std
            episode["angular_speed_mov_pos_p95"] = ang_mov_speed_pos_p95

        if (ang_speeds < 0).sum() > 1:
            ang_mov_speed_neg_mean = -ang_speeds[ang_speeds < 0].mean()
            ang_mov_speed_neg_std = -ang_speeds[ang_speeds < 0].std()
            ang_mov_speed_neg_p95 = np.percentile(-ang_speeds[ang_speeds < 0], 95)

            episode["angular_speed_mov_neg_mean"] = ang_mov_speed_neg_mean
            episode["angular_speed_mov_neg_std"] = ang_mov_speed_neg_std
            episode["angular_speed_mov_neg_p95"] = ang_mov_speed_neg_p95

    not_moving_bin = ~moving_bin
    if not_moving_bin.sum() > 0:
        ang_std_not_mov = ang_smooth[not_moving_bin].std()
        ang_p05_not_mov, ang_p95_not_mov = np.percentile(
            ang_smooth[not_moving_bin], (5, 95)
        )
        ang_mean_not_mov = ang_smooth[not_moving_bin].mean()
        episode["angle_non-moving_std"] = ang_std_not_mov
        episode["angle_non-moving_p05"] = ang_p05_not_mov
        episode["angle_non-moving_mean"] = ang_mean_not_mov
        episode["angle_non-moving_p95"] = ang_p95_not_mov

    return episode


def angle_correlation_episode(tad, episode, name, nodes_tuple, cfg):
    cfgs = cfg[episode.stage]
    frames = (episode.episode_start, episode.episode_stop)

    a_nodes, b_nodes = nodes_tuple

    a_ang = tadpose.analysis.angles(
        tad,
        (a_nodes[0], a_nodes[1]),
        (a_nodes[1], a_nodes[2]),
        track_idx=episode.track_idx,
        frames=frames,
    )
    b_ang = tadpose.analysis.angles(
        tad,
        (b_nodes[0], b_nodes[1]),
        (b_nodes[1], b_nodes[2]),
        track_idx=episode.track_idx,
        frames=frames,
    )

    a_ang_smooth = gaussian_filter1d(a_ang, cfgs["ANGLE_CORR_TEMP_ANGLE_SMOOTH"])
    a_ang_zscore = (a_ang_smooth - a_ang_smooth.mean()) / a_ang_smooth.std()

    b_ang_smooth = gaussian_filter1d(b_ang, cfgs["ANGLE_CORR_TEMP_ANGLE_SMOOTH"])
    b_ang_zscore = (b_ang_smooth - b_ang_smooth.mean()) / b_ang_smooth.std()

    if name.startswith("LR"):
        b_ang_zscore *= -1

    corr = tadpose.utils.corr_roll(
        a_ang_zscore, b_ang_zscore, win=cfgs["ANGLE_CORR_WIN_SIZE"]
    )
    a_ang_grad_mag = gaussian_filter1d(
        np.abs(np.gradient(a_ang_zscore)), cfgs["ANGLE_CORR_ACTIVE_SMOOTH"]
    )
    b_ang_grad_mag = gaussian_filter1d(
        np.abs(np.gradient(b_ang_zscore)), cfgs["ANGLE_CORR_ACTIVE_SMOOTH"]
    )

    ang_grad_mag = np.maximum(a_ang_grad_mag, b_ang_grad_mag)

    active_bin = ang_grad_mag > cfgs["ANGLE_CORR_ACTIVE_THRESH"]
    corr_active = corr[active_bin]

    corr_active = corr_active[~np.isnan(corr_active)]

    episode["name"] = name

    for c in [
        "corr_median",
        "corr_p05",
        "corr_p95",
        "corr_skewness",
        "corr_std",
        "computed_of_ratio",
    ]:
        episode[c] = None

    if len(corr_active) > 0:
        episode["corr_median"] = np.median(corr_active)
        episode["corr_p05"] = np.percentile(corr_active, 5)
        episode["corr_p95"] = np.percentile(corr_active, 95)
        episode["corr_skewness"] = skew(corr_active)
        episode["corr_std"] = corr_active.std()
        episode["computed_of_ratio"] = len(corr_active) / np.diff(frames)[0]

    return episode


def frequency_episode(tad, episode, name, nodes_tuple, sub_bgrd, cfg):
    cfgs = cfg[episode.stage]
    frames = (episode.episode_start, episode.episode_stop)
    scales, freq, wavelet, fps = get_frequency_params(cfg)

    tail_a, tail_b, tail_c = nodes_tuple

    mean_psd_moving, freq, computed_on = compute_angle_wavlet_psd_mean(
        tad,
        episode.track_idx,
        frames,
        scales,
        wavelet,
        tail_a,
        tail_b,
        tail_c,
        fps,
        sub_bgrd,
        cfgs,
    )

    dom_freq_prom = dominant_frequencies(mean_psd_moving, freq)

    freq_dom_split = 6
    if "FREQ_DOMINANT_SPLIT" in cfg:
        freq_dom_split = cfg["FREQ_DOMINANT_SPLIT"]

    dom_freq_prom_1 = (None, None, None)
    for f, p, ph in dom_freq_prom:
        if f and f <= freq_dom_split:
            dom_freq_prom_1 = (f, p, ph)
            break

    dom_freq_prom_2 = (None, None, None)
    for f, p, ph in dom_freq_prom:
        if f and f > freq_dom_split:
            dom_freq_prom_2 = (f, p, ph)
            break

    episode["name"] = name

    episode["dominant_freq"] = dom_freq_prom[0][0]
    episode["dominant_freq_prominence"] = dom_freq_prom[0][1]
    episode["dominant_freq_power"] = dom_freq_prom[0][2]
    episode[f"dominant_freq_{freq_dom_split}-"] = dom_freq_prom_1[0]
    episode[f"dominant_freq_prominence_{freq_dom_split}-"] = dom_freq_prom_1[1]
    episode[f"dominant_freq_power_{freq_dom_split}-"] = dom_freq_prom_1[2]
    episode[f"dominant_freq_{freq_dom_split}+"] = dom_freq_prom_2[0]
    episode[f"dominant_freq_prominence_{freq_dom_split}+"] = dom_freq_prom_2[1]
    episode[f"dominant_freq_power_{freq_dom_split}+"] = dom_freq_prom_2[2]
    episode["freq_active_ratio"] = computed_on

    for k, v in zip(freq, mean_psd_moving):
        episode[k] = v

    return episode


def locomotion_episode(tad, episode, cfg):
    from tadpose.utils import directional_change

    cfgs = cfg[episode.stage]
    frames = (episode.episode_start, episode.episode_stop)
    episode_duration = np.diff(frames)[0]

    speed_px_per_frame = tad.speed(
        cfgs["LOCOMOTION_NODE"],
        track_idx=episode.track_idx,
        pre_sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
        sigma=cfgs["LOCOMOTION_TEMPORAL_SIGMA"],
        frames=frames,
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

    time_spent_moving = moving_bin.sum() / episode_duration

    total_dist = speed_calib[moving_bin].sum() / cfg["FPS"]

    acceleration = np.gradient(speed_calib)

    part_loc = tad.locs(
        parts=(cfgs["LOCOMOTION_NODE"],), track_idx=episode.track_idx
    ).squeeze()[frames[0] : frames[1]]

    dc_angles = directional_change(
        part_loc,
        sigma=cfgs["LOCOMOTION_SPATIAL_SIGMA"],
        subsample=cfgs["LOCOMOTION_DC_SUBSAMPLE"],
    )

    moving_sub = moving_bin[:: cfgs["LOCOMOTION_DC_SUBSAMPLE"]][1:-1]

    for c in [
        "speed_moving_mean",
        "speed_moving_std",
        "speed_moving_p95",
        "time_spent_moving_ratio",
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
        "total_distance",
    ]:
        episode[c] = None

    if np.any(moving_sub):
        dc_mov = dc_angles[moving_sub]
        dc_abs = np.abs(dc_mov)
        dc_pos = dc_mov[dc_mov > 0]
        dc_neg = np.abs(dc_mov[dc_mov < 0])

        if len(dc_abs) > 1:
            episode["directional_change_mean"] = dc_abs.mean()
            episode["directional_change_std"] = dc_abs.std()
            episode["directional_change_95"] = np.percentile(dc_abs, 95)

        if len(dc_pos) > 1:
            episode["directional_change_pos_mean"] = dc_pos.mean()
            episode["directional_change_pos_std"] = dc_pos.std()
            episode["directional_change_pos_95"] = np.percentile(dc_pos, 95)

        if len(dc_neg) > 1:
            episode["directional_change_neg_mean"] = dc_neg.mean()
            episode["directional_change_neg_std"] = dc_neg.std()
            episode["directional_change_neg_95"] = np.percentile(dc_neg, 95)

    if time_spent_moving > 0:
        episode["speed_moving_mean"] = speed_calib[moving_bin].mean()
        episode["speed_moving_std"] = speed_calib[moving_bin].std()
        episode["speed_moving_p95"] = np.percentile(speed_calib[moving_bin], 95)

    if (acceleration > 0).sum() > 1:
        episode["acceleration_mean"] = acceleration[acceleration > 0].mean()
        episode["acceleration_p95"] = np.percentile(acceleration[acceleration > 0], 95)

    episode["total_distance"] = total_dist
    episode["time_spent_moving_ratio"] = time_spent_moving * 100

    return episode


def compute_angle_wavlet_psd_mean(
    tad, tid, frames, scales, wavelet, a, b, c, fps, sub_bgrd, cfgs
):
    ang = tadpose.analysis.angles(tad, (a, b), (b, c), frames=frames, track_idx=tid)
    ang_smooth = gaussian_filter1d(ang, cfgs["FREQ_TEMP_ANGLE_SMOOTH"])

    if sub_bgrd:
        ang_background = gaussian_filter1d(ang, cfgs["FREQ_ACTIVE_SMOOTH"])
    else:
        ang_background = 0

    ang_smooth -= ang_background

    ang_zscore = (ang_smooth - ang_smooth.mean()) / ang_smooth.std()

    cwt_coeff, freq = pywt.cwt(
        ang_zscore,
        scales,
        wavelet,
        sampling_period=1 / fps,
        method="fft",
    )

    t_wvlt_psd = np.abs(cwt_coeff * np.conj(cwt_coeff)).T

    ang_grad_mag = gaussian_filter1d(
        np.abs(np.gradient(ang_zscore)), cfgs["FREQ_ACTIVE_SMOOTH"]
    )

    moving_bin = ang_grad_mag > cfgs["FREQ_ACTIVE_THRESH"]

    computed_on = moving_bin.sum() / tad.nframes

    if moving_bin.sum() > 1:
        mean_psd_moving = t_wvlt_psd[moving_bin].mean(0)
    else:
        mean_psd_moving = np.nan

    return mean_psd_moving, freq, computed_on


def dominant_frequencies(sig, freq, n_peaks=2):
    peaks, props = signal.find_peaks(sig, height=(None, None), prominence=(None, None))

    res = [(None, None, None)] * n_peaks
    for k, pp in enumerate(range(min(len(peaks), n_peaks))):
        peak_pos = np.argsort(
            props["peak_heights"],
        )[-1 - pp]
        dom_f = freq[peaks[peak_pos]]
        dom_p = props["prominences"][peak_pos]
        dom_ph = props["peak_heights"][peak_pos]
        res[k] = (dom_f, dom_p, dom_ph)
    return res


def get_frequency_params(cfg):
    N = cfg["FREQUENCY_N"]
    wavelet = cfg["FREQUENCY_WAVELET"]

    # Fc = pywt.central_frequency(wavelet)
    fps = cfg["FPS"]
    sp = 1 / fps

    scales = 2 ** np.linspace(1, 6, N)  # <- dyadic 1-30HZ
    frequencies = pywt.scale2frequency(wavelet, scales) / sp
    return scales, frequencies, wavelet, fps
