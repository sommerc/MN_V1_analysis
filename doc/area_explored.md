# Area explored features
---

## Basics

Area explored features quantify the spatial extent to which the frog has explored the dish. A SLEAP-tracked body-part is used as a proxy to compute *area explored* features.

### Setup and settings

For the analysis two settings need to be set in the settings YAML file. These entries need be specified in each `STAGE_GRP` section. For instance:

```yaml
  AREA_EXPLORED_NODE: "Tail_1"
  AREA_EXPLORED_BINS: 128
```

We measure the ratio of dish area explored by the frog by selecting a central SLEAP-tracked body-part `AREA_EXPLORED_NODE` and building the 2D histogram of its trajectory at given bin-size. The square containing the circular dish ROI was discretized into `AREA_EXPLORED_BINS` x `AREA_EXPLORED_BINS` 2D bins. The 2D location histogram of the selected body-part is built over those bins. Each bin contains the number of times the location of the body-part was overlapping with this bin over its trajectory. Hence, a bin with value zero was never visited. The ratio of *area explored* is built by the number of bins visited divided by the total number of bins. 

To make movies of different length comparable, we further normalize this ratio to per hour.

Visualization of the histogram are stored in `RESULTS_ROOT_DIR/AREA_EXPLORED_OUTDIR/imgs`. 


## Run specifically

Result tables and plots are stored in `RESULTS_ROOT_DIR/AREA_EXPLORED_OUTDIR` (default: ./area_explored)

```bash
# Generate output tables
python area_explored_analysis.py

# Basic plots per Stages and Genotypes
python area_explored_plots.py
```

## Computed features

| Feature              | Description                                                          | 
| :----------------    | :------------------------------------------------         | 
|area_explored_ratio   | From the 2D histogram, the relative count of non-zeros bins is computed. |
|area_explored_per_h   | To make movies of different lengths comparable, `area_explored_ratio` is normalized by the length of the movie. |

