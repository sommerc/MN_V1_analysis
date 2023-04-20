
# Angle Range Analysis
---
## Basics
Angle range features extract information about the variance of angle distributions at defined body-part segments.

### More to come

## Run specifically with default `analysis_settings.yml`:
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