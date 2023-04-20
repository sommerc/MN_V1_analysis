import os
import h5py
import yaml

import numpy as np
from scipy.ndimage import gaussian_filter1d


def settings(config_yml=None):
    if config_yml is None:
        config_yml = "H:/projects/068_lora_tadpole/paper_code/analysis_settings.yml"

    print(f"Using settings '{config_yml}'")

    with open(config_yml, "r") as ymlfile:
        config_dict = yaml.safe_load(ymlfile)

    for key in config_dict.keys():
        result_root = config_dict["RESULTS_ROOT_DIR"]
        if key.endswith("_OUTDIR"):
            config_dict[key] = os.path.join(result_root, config_dict[key])

    return config_dict


# def get_good_tracks(fn, cfgs, node=None):
#     with h5py.File(fn, "r") as hf:
#         n_tracks, _, n_skel, n_frames = hf["tracks"].shape
#         tracks = hf["tracks"]
#         if node is None:
#             track_is_lost = np.any(np.isnan(tracks), axis=(1, 2)).sum(1) / n_frames
#             track_okay_idx = np.nonzero(track_is_lost < cfgs["TRACK_SELECT_THRES"])[0]
#         else:
#             for i, n in enumerate(hf["node_names"]):
#                 if n.decode() == node:
#                     break
#             else:
#                 raise RuntimeError(f"Node {node} not found")

#             track_is_lost = (
#                 np.any(np.isnan(tracks[:, :, i]), axis=(1,)).sum(1) / n_frames
#             )
#             track_okay_idx = np.nonzero(track_is_lost < cfgs["TRACK_SELECT_THRES"])[0]

#     return track_okay_idx


def angles(vec1, vec2):
    EPS = 0.000000000001
    vec1 = (vec1.T / (np.linalg.norm(vec1, axis=1) + EPS)).T
    vec2 = (vec2.T / (np.linalg.norm(vec2, axis=1) + EPS)).T

    ortho_vec1 = np.c_[-vec1[:, 1], vec1[:, 0]]
    sign = np.sign(np.sum(ortho_vec1 * vec2, axis=1))

    c = np.sum(vec1 * vec2, axis=1)
    angles = sign * np.rad2deg(np.arccos(np.clip(c, -1, 1)))
    return angles


def directional_change(xy, sigma=None, subsample=2):
    if sigma is not None:
        xy_smo = gaussian_filter1d(xy, sigma=sigma, axis=0)
    else:
        xy_smo = xy

    xy_smo = xy_smo[::subsample]
    v = np.diff(xy_smo, axis=0)
    return np.abs(angles(v[:-1], v[1:]))
