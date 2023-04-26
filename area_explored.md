# Area Explored Analysis
---
## Basics
Area explored features extract information about how the area of the dish has explored by the frog. A proxy SLEAP-tracked body-part is used to compute the area explored

### Setup and settings
For the area explored analysis, two settings need to be set in the settings YAML file. These entries need be specified in each `STAGE_GRP` section.

```
  AREA_EXPLORED_NODE: "Tail_1"
  AREA_EXPLORED_BINS: 128
```

The `AREA_EXPLORED_NODE` defines which body-part is used. The square containing the circular dish roi (, which annotates the dish) is discretized into `AREA_EXPLORED_BINS` x `AREA_EXPLORED_BINS` 2D bins. A 2D dimension histogram of the selected body-part is built over these bins. Each bin contains the number of times the location of the body-part was overlapping with this bin. A bin with value zero was never *visited*. 

Visualization of the histogram are stored in `RESULTS_ROOT_DIR/AREA_EXPLORED_OUTDIR/imgs`. 


## Run specifically
Result tables and plots are stored in `RESULTS_ROOT_DIR/AREA_EXPLORED_OUTDIR` (default: ./area_explored)
```
# Generate output tables
python area_explored_analysis.py

# Basic plots per Stages and Genotypes
python area_explored_plots.py
```

## Computed features

### area_explored_ratio
From the 2D histogram, the relative count of non-zeros bins is computed.

### area_explored_per_h
To make movies of different lengths comparable, `area_explored_ratio` is normalized by the length of the movie.