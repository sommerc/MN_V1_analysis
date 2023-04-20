# Area Explored Analysis
---
## Basics
Area explored features extract information about the dish coverage of an SLEAP-tracked body-part. 

### More to come

## Run specifically with default `analysis_settings.yml`:
Result tables and plots are stored in `RESULTS_ROOT_DIR/AREA_EXPLORED_OUTDIR` (default: ./area_explored)
```
# Generate output tables
python area_explored_analysis.py

# Basic plots per Stages and Genotypes
python area_explored_plots.py
```

## Computed features

### area_explored_ratio
The ratio of area inside the dish, which the frog visited.

### area_explored_per_h
The ratio of area inside the dish, normalized to the to hour. This is needed since, movies may not be of the same length.