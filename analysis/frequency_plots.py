import os
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import colors as mpl_colors
from tqdm.auto import tqdm, trange

from shared import settings


def plot_by_stage(cfg):
    OUT_DIR = cfg["FREQUENCY_OUTDIR"]
    TAB = pd.read_csv(f"{OUT_DIR}/frequency_res.tab", sep="\t", index_col=0)
    STAGES = TAB.Stage.unique()
    FREQ_FOR = TAB.frequency_for.unique()

    OUT_DIR = cfg["FREQUENCY_OUTDIR"]

    for stg in STAGES:
        for freq_for in FREQ_FOR:
            tab_sub = TAB[(TAB.Stage == stg) & (TAB.frequency_for == freq_for)]
            if len(tab_sub) > 0:
                f, ax = plt.subplots(
                    1, tab_sub.Genotype.nunique(), sharey=True, figsize=(20, 4)
                )
                try:
                    ax[0]
                except:
                    ax = [ax]

                cc = ax[0]._get_lines.prop_cycler

                for i, (gen, tab) in enumerate(tab_sub.groupby("Genotype")):
                    a = tab.T.iloc[8:-1].mean(1)
                    b = tab.T.iloc[8:-1].std(1)
                    x_vals = a.index.astype("float")
                    color = next(cc)["color"]
                    ax[i].plot(x_vals, a, color=color)
                    ax[i].fill_between(x_vals, (a - b), (a + b), alpha=0.3, color=color)
                    ax[i].set_title(gen)
                    ax[i].set_ylim(0, 16)
                    sns.despine(ax=ax[i])
                    ax[i].set_xlabel(f"Frequency of angle change at {freq_for}")
                    ax[i].set_ylabel("Mean CWT power spectrum")
                plt.tight_layout()

                plt.savefig(f"{OUT_DIR}/{stg}_{freq_for}_cwt_mean_ps.pdf")
                plt.close(f)

                feature = "dominant_freq"
                f, ax = plt.subplots(figsize=(14, 4))

                if np.all(np.isnan(tab_sub[feature])):
                    ax.set_xlabel("No dominant frequency peaks could be detected")
                else:
                    b = sns.stripplot(
                        y=feature,
                        x="Genotype",
                        data=tab_sub,
                        ax=ax,
                        hue="Genotype",
                        dodge=False,
                        zorder=1,
                        legend=False,
                    )
                sns.despine(ax=ax)
                ax.set_title(f"{stg}_{freq_for}")
                plt.savefig(f"{OUT_DIR}/{stg}_{freq_for}_dominant_cwt_freq.pdf")
                plt.close(f)

                f, ax = plt.subplots(figsize=(8, 8))

                if np.all(np.isnan(tab_sub["dominant_freq"])):
                    ax.set_xlabel("No dominant frequency peaks could be detected")
                else:
                    sns.scatterplot(
                        x="dominant_freq",
                        y="dominant_freq_prominence",
                        size="freq_active_ratio",
                        data=tab_sub,
                        hue="Genotype",
                        legend="brief",
                        edgecolor="none",
                        alpha=0.8,
                    )
                sns.despine(ax=ax)
                ax.set_title(f"{stg}_{freq_for}")
                plt.savefig(f"{OUT_DIR}/{stg}_{freq_for}_dominant+prominence_freq.pdf")
                plt.close(f)


def plot_by_geno(cfg):
    OUT_DIR = cfg["FREQUENCY_OUTDIR"]
    TAB = pd.read_csv(f"{OUT_DIR}/frequency_res.tab", sep="\t", index_col=0)

    GENO = TAB.Genotype.unique()
    FREQ_FOR = TAB.frequency_for.unique()

    OUT_DIR = cfg["FREQUENCY_OUTDIR"]

    for gen in GENO:
        for freq_for in FREQ_FOR:
            tab_sub = TAB[(TAB.Genotype == gen) & (TAB.frequency_for == freq_for)]
            if len(tab_sub) > 0:
                f, ax = plt.subplots(
                    1, tab_sub.Stage.nunique(), sharey=True, figsize=(20, 4)
                )
                try:
                    ax[0]
                except:
                    ax = [ax]

                cc = ax[0]._get_lines.prop_cycler

                for i, (stg, tab) in enumerate(tab_sub.groupby("Stage")):
                    a = tab.T.iloc[8:-1].mean(1)
                    b = tab.T.iloc[8:-1].std(1)
                    x_vals = a.index.astype("float")
                    color = next(cc)["color"]
                    ax[i].plot(x_vals, a, color=color)
                    ax[i].fill_between(x_vals, (a - b), (a + b), alpha=0.3, color=color)
                    ax[i].set_title(stg)
                    ax[i].set_ylim(0, 16)
                    sns.despine(ax=ax[i])
                    ax[i].set_xlabel(f"Frequency of angle change at {freq_for}")
                    ax[i].set_ylabel("Mean CWT power spectrum")
                plt.tight_layout()

                plt.savefig(f"{OUT_DIR}/{gen}_{freq_for}_cwt_mean_ps.pdf")
                plt.close(f)

                feature = "dominant_freq"
                f, ax = plt.subplots(figsize=(14, 4))

                if np.all(np.isnan(tab_sub[feature])):
                    ax.set_xlabel("No dominant frequency peaks could be detected")
                else:
                    b = sns.stripplot(
                        y=feature,
                        x="Stage",
                        data=tab_sub,
                        ax=ax,
                        hue="Stage",
                        dodge=False,
                        zorder=1,
                        legend=False,
                    )

                sns.despine(ax=ax)
                ax.set_title(f"{gen}_{freq_for}")
                plt.savefig(f"{OUT_DIR}/{gen}_{freq_for}_dominant_cwt_freq.pdf")
                plt.close(f)

                f, ax = plt.subplots(figsize=(8, 8))

                if np.all(np.isnan(tab_sub[feature])):
                    ax.set_xlabel("No dominant frequency peaks could be detected")
                else:
                    sns.scatterplot(
                        x="dominant_freq",
                        y="dominant_freq_prominence",
                        size="freq_active_ratio",
                        data=tab_sub,
                        hue="Stage",
                        legend="brief",
                        edgecolor="none",
                        alpha=0.8,
                    )
                sns.despine(ax=ax)
                ax.set_title(f"{gen}_{freq_for}")
                plt.savefig(f"{OUT_DIR}/{gen}_{freq_for}_dominant+prominence_freq.pdf")
                plt.close(f)


def plot(cfg):
    plot_by_geno(cfg)
    plot_by_stage(cfg)


if __name__ == "__main__":
    cfg = settings()

    plot(cfg)
