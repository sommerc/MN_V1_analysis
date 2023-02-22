import os
import yaml
import numpy as np
import pandas as pd
import pathlib
from typing import Dict, Any


def load_metrics(model_path: str, split: str = "val") -> Dict[str, Any]:
    """Load metrics for a model.
    Args:
        model_path: Path to a model folder or metrics file (.npz).
        split: Name of the split to load the metrics for. Must be `"train"`, `"val"` or
            `"test"` (default: `"val"`). Ignored if a path to a metrics NPZ file is
            provided.
    Returns:
        The loaded metrics as a dictionary with keys:
        - `"vis.tp"`: Visibility - True Positives
        - `"vis.fp"`: Visibility - False Positives
        - `"vis.tn"`: Visibility - True Negatives
        - `"vis.fn"`: Visibility - False Negatives
        - `"vis.precision"`: Visibility - Precision
        - `"vis.recall"`: Visibility - Recall
        - `"dist.avg"`: Average Distance (ground truth vs prediction)
        - `"dist.p50"`: Distance for 50th percentile
        - `"dist.p75"`: Distance for 75th percentile
        - `"dist.p90"`: Distance for 90th percentile
        - `"dist.p95"`: Distance for 95th percentile
        - `"dist.p99"`: Distance for 99th percentile
        - `"dist.dists"`: All distances
        - `"pck.mPCK"`: Mean Percentage of Correct Keypoints (PCK)
        - `"oks.mOKS"`: Mean Object Keypoint Similarity (OKS)
        - `"oks_voc.mAP"`: VOC with OKS scores - mean Average Precision (mAP)
        - `"oks_voc.mAR"`: VOC with OKS scores - mean Average Recall (mAR)
        - `"pck_voc.mAP"`: VOC with PCK scores - mean Average Precision (mAP)
        - `"pck_voc.mAR"`: VOC with PCK scores - mean Average Recall (mAR)
    """
    if os.path.isdir(model_path):
        metrics_path = os.path.join(model_path, f"metrics.{split}.npz")
    else:
        metrics_path = model_path
    with np.load(metrics_path, allow_pickle=True) as data:
        return data["metrics"].item()


with open("constants.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)


STAGES = [
    "37-38",
    "44-48",
    "52-54",
    "57-58",
    "59-62",
    "63-64",
    "Juv",
]

METRICS = [
    "vis.precision",
    "vis.recall",
    "dist.avg",
    "dist.p50",
    "pck.mPCK",
    "oks.mOKS",
]

res = []
for stg in STAGES:
    model_path = pathlib.Path(cfg[stg]["ROOT_DIR"]) / "models"

    try:
        metrics_centr_fn = next(model_path.glob("*centroid*"))
        metrics_centr = load_metrics(metrics_centr_fn)
        for met in METRICS:
            res.append([stg, met, "Centroid", metrics_centr[met], metrics_centr_fn])
    except FileNotFoundError:
        res.append([stg, met, "Centroid", np.nan, np.nan])

    try:
        metrics_insta_fn = next(model_path.glob("*centered_instance*"))
        metrics_insta = load_metrics(metrics_insta_fn)
        for met in METRICS:
            res.append([stg, met, "Instance", metrics_insta[met], metrics_insta_fn])
    except FileNotFoundError:
        res.append([stg, met, "Instance", np.nan, np.nan])


tab = pd.DataFrame(res, columns=["Stage", "Metric", "Type", "Value", "Path"])
tab.to_csv("metrics_validation.tab", sep="\t")
