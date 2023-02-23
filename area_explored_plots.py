import os
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import colors as mpl_colors
from tqdm.auto import tqdm, trange

from shared import settings

def plot_by_stage(cfg):
    
    STAGES = [
        "37-38",
        "44-48",
        "52-54",
        "57-58",
        "59-62",
        "63-64",
        "Juv",
    ]
    OUT_DIR = cfg["AREA_EXPLORED_OUTDIR"]

    for STAGE in STAGES:
        tab_stg = pd.read_csv(
            f"{cfg['AREA_EXPLORED_OUTDIR']}/area_explored_{STAGE}_res.tab", sep="\t"
        )

        for feature in [
            "area_explored_per_h"
            
        ]:
            f, ax = plt.subplots(figsize=(14,4))
            a = sns.boxenplot(
                y=feature,
                x="Genotype",
                data=tab_stg,
                ax=ax,
                hue="Genotype",
                box_kws={"alpha":0.4},
                dodge=False

            )
            a.legend_.remove()
            b = sns.stripplot(
                y=feature,
                x="Genotype",
                data=tab_stg,
                ax=ax,
                hue="Genotype",
                dodge=False,
                zorder=1, legend=False
            )
            sns.despine(ax=ax)
            ax.set_title(f"{STAGE} {feature}")
            plt.savefig(f"{OUT_DIR}/{STAGE}_{feature}.pdf", bbox_inches="tight")
            plt.close(f)

        
def plot_by_geno(cfg):
    TAB = pd.read_csv("area_explored/area_explored_res.tab", sep="\t", index_col=0)

    GENO = TAB.Genotype.unique()

    OUT_DIR = cfg["AREA_EXPLORED_OUTDIR"]

    for gen in GENO:
        tab_sub = TAB[(TAB.Genotype == gen)]
        if len(tab_sub) > 0:
            for feature in [
                "area_explored_per_h"
                
            ]:
                f, ax = plt.subplots(figsize=(14,4))
                a = sns.boxenplot(
                    y=feature,
                    x="Stage",
                    data=tab_sub,
                    ax=ax,
                    hue="Stage",
                    box_kws={"alpha":0.4},
                    dodge=False

                )
                a.legend_.remove()
                b = sns.stripplot(
                    y=feature,
                    x="Stage",
                    data=tab_sub,
                    ax=ax,
                    hue="Stage",
                    dodge=False,
                    zorder=1, legend=False
                )
                sns.despine(ax=ax)
                ax.set_title(f"{gen} {feature}")
                plt.savefig(f"{OUT_DIR}/{gen}_{feature}.pdf", bbox_inches="tight")
                plt.close(f)

if __name__ == "__main__":
    cfg = settings()
    plot_by_geno(cfg)
    plot_by_stage(cfg)
    
    