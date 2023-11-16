import os
import shutil
import yaml

import numpy as np
from scipy.ndimage import gaussian_filter1d


def settings(config_yml=None):
    if config_yml is None:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
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

    shutil.copy(config_yml, f'{config_dict["RESULTS_ROOT_DIR"]}/used_settings.yaml')

    return config_dict


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
