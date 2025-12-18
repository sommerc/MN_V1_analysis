from pathlib import Path
import functools
import yaml

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

import tadpose as tp
from features import (
    angle_correlation_episode,
    angle_range_episode,
    frequency_episode,
    locomotion_episode,
)


def check_epi_bound(value, default):
    if isinstance(value, float) and np.isnan(value):
        value = default
    if isinstance(value, float):
        value = int(value)
    if isinstance(value, (int, float)) and value < 0:
        value = 0

    return value


@functools.cache
def get_tad(fn):
    return tp.Tadpole.from_sleap(fn)


def analyze_episodes(tab_fn, cfg):
    episode_tab = pd.read_csv(tab_fn, sep="\t", index_col=0)

    AC_RESULTS = []
    AR_RESULTS = []
    F_RESULTS = []
    F_BS_RESULTS = []
    L_RESULTS = []

    n = len(episode_tab)
    i = 0
    for _, row in (pbar := tqdm(episode_tab.iterrows(), total=n)):
        print(f"{i:5d}/{n}", row.video_fn, row.episode_start, row.episode_stop)
        tad = get_tad(row.video_fn)
        cfgs = cfg[row.stage]

        row.episode_start = check_epi_bound(row.episode_start, 0)
        row.episode_stop = check_epi_bound(row.episode_stop, tad.nframes)

        pbar.set_description(
            f"Processing {Path(row.video_fn).name} for episode {row.episode_start}-{row.episode_stop}"
        )

        ### Angle Correlation
        ######################################################################################
        if "ANGLE_CORR_FOR" in cfgs:
            for name, nodes_tuple in cfgs["ANGLE_CORR_FOR"].items():
                ac_episode_result = angle_correlation_episode(
                    tad, row.copy(), name, nodes_tuple, cfg=cfg
                )
                AC_RESULTS.append(ac_episode_result)

        ### Angle Range
        ######################################################################################
        if "ANGLE_RANGE_FOR" in cfgs:
            for name, nodes_tuple in cfgs["ANGLE_RANGE_FOR"].items():
                ar_episode_result = angle_range_episode(
                    tad, row.copy(), name, nodes_tuple, cfg=cfg
                )
                AR_RESULTS.append(ar_episode_result)

        ### Frequency
        ######################################################################################
        if "FREQ_FOR" in cfgs:
            for name, nodes in cfgs["FREQ_FOR"].items():
                f_episode_result = frequency_episode(
                    tad, row.copy(), name, nodes, False, cfg=cfg
                )
                F_RESULTS.append(f_episode_result)

        ### Frequency Background Subtracted
        ######################################################################################
        if "FREQ_FOR" in cfgs:
            for name, nodes in cfgs["FREQ_FOR"].items():
                f_episode_result = frequency_episode(
                    tad, row.copy(), name, nodes, True, cfg=cfg
                )
                F_BS_RESULTS.append(f_episode_result)

        ### Locomation
        ######################################################################################
        l_episode_result = locomotion_episode(tad, row.copy(), cfg=cfg)
        L_RESULTS.append(l_episode_result)
        i += 1

    PREFIX = str(Path(tab_fn).parent) + "/"
    AC_RESULTS = pd.DataFrame(AC_RESULTS).to_csv(f"{PREFIX}_AC_res.tab", sep="\t")
    AR_RESULTS = pd.DataFrame(AR_RESULTS).to_csv(f"{PREFIX}_AR_res.tab", sep="\t")
    F_RESULTS = pd.DataFrame(F_RESULTS).to_csv(f"{PREFIX}_FREQ_res.tab", sep="\t")
    F_BS_RESULTS = pd.DataFrame(F_BS_RESULTS).to_csv(
        f"{PREFIX}_FREQ_BS_res.tab", sep="\t"
    )
    L_RESULTS = pd.DataFrame(L_RESULTS).to_csv(f"{PREFIX}_LOC_res.tab", sep="\t")


if __name__ == "__main__":
    cfg_fn = (
        "H:/projects/068_lora_tadpole/paper_code/analysis_settings_test_episdodes.yml"
    )
    epi_fn = "H:/projects/068_lora_tadpole/tadpose/notebooks/straight_movement_episodes/data/_straight_line_episodes.tab"

    with open(cfg_fn, "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    analyze_episodes(epi_fn, cfg)
