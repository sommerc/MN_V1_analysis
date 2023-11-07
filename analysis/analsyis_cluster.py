import sys
import argparse

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
    parser = argparse.ArgumentParser(description="Frog-Analysis cluster analysis run")

    parser.add_argument(
        "-t",
        "--type",
        help="Type of Analysis: L, F, P, AE, AR, or AC",
        type=str,
        required=True,
    )

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

    if args.type.lower() == "l":
        print("LOCOMOTION")
        locomotion_analysis(cfg)
        locomotion_plots(cfg)
    elif args.type.lower() == "f":
        print("FREQUENCY")
        frequency_plots(cfg)
        frequency_plots(cfg)
    elif args.type.lower() == "p":
        print("PCA PLOTS")
        pca_moving_plots(cfg)
    elif args.type.lower() == "ae":
        print("AREA EXPLORED")
        area_explored_analysis(cfg)
        area_explored_plot(cfg)
    elif args.type.lower() == "ae":
        print("ANGLE RANGE")
        angle_range_analysis(cfg)
        angle_range_plots(cfg)
    elif args.type.lower() == "ac":
        print("ANGLE RANGE")
        angle_correlation_analysis(cfg)
        angle_correlation_plots(cfg)
    else:
        print(
            f"ERROR: analysis type {args.type} not understood. choose L, F, P, AE, AR, or AC"
        )
