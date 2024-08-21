
# Angle Range Analysis
---
## Basics
Angle range features extract information about the variance of angle distributions at defined body-part segments.

### Setup and settings
For the angle range analysis, three settings need to be set in the settings YAML file. These entries need be specified in each `STAGE_GRP` section.

```python
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

```bash
# Generate output tables
python angle_range_analysis.py

# Basic plots per Stages and Genotypes
python angle_range_plots.py
```

## Computed features

| Feature              | Description                                               | 
| :----------------    | :------------------------------------------------         | 
| angle_moving_std  | std of angles during moving episodes (degree)                |
| angle_moving_p05  | 56h of angles during moving episodes                         |
| angle_moving_mean | mean of angles during moving episodes                        |
| angle_moving_p95  | 95th of angles during moving episodes                        |
| angle_non-moving_std  | std of angles during non-moving episodes (degree) |
| angle_non-moving_p05  | 56h of angles during non-moving episodes  |
| angle_non-moving_mean | mean of angles during non-moving episodes |
| angle_non-moving_p95  | 95th of angles during non-moving episodes |
| angular_speed_mov_pos_mean  | mean angular speed of regarding only positive values during moving episodes |
| angular_speed_mov_pos_std,  | std angular speed of regarding only positive values during moving episodes  |
| angular_speed_mov_pos_p95,  | 95th angular speed of regarding only positive values during moving episodes   |
| angular_speed_mov_neg_mean  | same as above but using negative angular speed values only |
| angular_speed_mov_neg_std,  |  same as above but using negative angular speed values only |
| angular_speed_mov_neg_p95,  | same as above but using negative angular speed values only  |
| angle_at  | body-part at which the angle was computed         |