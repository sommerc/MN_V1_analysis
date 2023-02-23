from multiprocessing import Process

from area_explored_analysis import main as area_explored_analysis
from locomotion_analysis import main as locomotion_analysis
from frequency_analysis import main as frequency_analysis
from angle_range_analysis import main as angle_range_analysis
from pca_moving_plots import main as pca_moving_plots

from area_explored_plots import plot as aep
from angle_range_plots import plot as arp
from frequency_plots import plot as fp
from locomotion_plots import plot as lp

from shared import settings

if __name__ == "__main__":
    analysis_run = {
        "angle_range_analysis": angle_range_analysis,
        "area_explored_analysis": area_explored_analysis,
        "locomotion_analysis": locomotion_analysis,
        "frequency_analysis": frequency_analysis,
        "pca_moving_plots": pca_moving_plots,
    }

    res = []
    for name, func in analysis_run.items():
        print("Started", name)
        p1 = Process(target=func)
        p1.start()
        res.append(p1)

    for r in res:
        r.join()

    cfg = settings()
    lp(cfg)
    arp(cfg)
    aep(cfg)
    fp(cfg)
