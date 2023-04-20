import sys
import argparse
from multiprocessing import Process

from angle_correlation_analysis import main as angle_correlation_analysis
from angle_correlation_plots import plot as angle_correlation_plots

from angle_range_analysis import main as angle_range_analysis
from angle_range_plots import plot as angle_range_plots

from area_explored_analysis import main as area_explored_analysis
from area_explored_plots import plot as area_explored_plot

from frequency_analysis import main as frequency_analysis
from frequency_plots import plot as frequency_plots

from locomotion_analysis import main as locomotion_analysis
from locomotion_plots import plot as locomotion_plots

from pca_moving_plots import main as pca_moving_plots

from shared import settings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frog-Analysis main analyis run")
    parser.add_argument(
        "-s", "--settings", help="Settings YAML file", default=None, type=str
    )

    parser.add_argument(
        "-o", "--out_dir", help="Output root folder", default=None, type=str
    )

    args = parser.parse_args()

    cfg = settings(args.settings)

    if args.out_dir is not None:
        print(f" - Set 'RESULTS_ROOT_DIR' to '{args.out_dir}'")
        cfg["RESULTS_ROOT_DIR"] = args.out_dir

    analysis_run = {
        "angle_range_analysis": angle_range_analysis,
        "area_explored_analysis": area_explored_analysis,
        "locomotion_analysis": locomotion_analysis,
        "frequency_analysis": frequency_analysis,
        "pca_moving_plots": pca_moving_plots,
        "angle_correlation": angle_correlation_analysis,
    }

    res = []
    for name, func in analysis_run.items():
        print(" - Started", name)
        p1 = Process(target=func, args=(cfg,))
        p1.start()
        res.append(p1)

    for r in res:
        r.join()

    area_explored_plot(cfg)
    angle_range_plots(cfg)
    frequency_plots(cfg)
    locomotion_plots(cfg)
    angle_correlation_plots(cfg)
