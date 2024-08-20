
# Angle Range Analysis
---
## Basics
Angle range features extract information about the variance of angle distributions at defined body-part segments.

### Setup and settings
For the angle range analysis, three settings need to be set in the settings YAML file. These entries need be specified in each `STAGE_GRP` section.

```
  ANGLE_RANGE_MOVING_NODE: "Tail_1"
  ANGLE_RANGE_MOVING_NODE_THRESH: 1.2
  
  ANGLE_RANGE_FOR:
    tail_2:
      - Tail_1
      - Tail_2 # <- Angle here
      - Tail_3

```

## Run specifically:
Result tables and plots are stored in `RESULTS_ROOT_DIR/ANGLE_RANGE_OUTDIR` (default: ./angle_range)

```
# Generate output tables
python angle_range_analysis.py

# Basic plots per Stages and Genotypes
python angle_range_plots.py
```

## Computed features

### angle_std
                
The standard deviation of angles

### angle_moving_std
The standard deviation of angles from only *moving* episodes (see [locomotion](./locomotion.md))