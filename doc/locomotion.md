# Locomotion features
---
## Basics
Locomotion features extract information about the basic movement of a SLEAP-tracked body-part. Due to noise in the images, SLEAP body-part locations may exhibit dislocations of up-to few pixels. To make the locomotion analysis robust custom pre-processing is applied. The parameters of the pre-processing steps can be set in the settings YAML file.

### Setup and settings
For the locomotion analysis settings for each `STAGE_GRP` section must be provided. For instance:

```python
  LOCOMOTION_NODE: "Tail_1"
  LOCOMOTION_MOVING_THRESH: 1.2 # (cm/sec)
  LOCOMOTION_TEMPORAL_SIGMA: 30 # (frame)
  LOCOMOTION_SPATIAL_SIGMA: 1   # (frame)
  LOCOMOTION_DC_SUBSAMPLE: 8
```

### Definition of *moving* vs. *not-moving* episodes
To partition the time-course of an tracked animal into *moving* and *non-moving*, we first extract the yx-locations of the chosen body part from the SLEAP analysis HDF5 file. If the body part was not detected in all frames, we interpolate the missing frames using `numpy.interp`. Next, we apply a Gaussian smoothing to the y and x body-part locations using `skimage.filters.gaussian`, with the sigma set to `LOCOMOTION_SPATIAL_SIGMA` (default 1). The resulting smoothed locations are used to compute the instantaneous speed by central differences with `numpy.gradient`. We then smooth the resulting speed with a Gaussian with sigma=`LOCOMOTION_TEMPORAL_SIGMA` (default 30). Each frame is associated with a speed in pixels per frame, which we calibrate to cm per frame using the known diameter of the dish (14 cm) and the camera speed with frames-per-second (FPS) of 60 hz. Each dish was manually annotated with a circle ROI in ImageJ/Fiji.Finally, we threshold the calibrated speed by `LOCOMOTION_MOVING_THRESH` (default 1.2 cm/sec) to obtain a binary partitioning into moving vs. non-moving animal episodes.

### Speed and acceleration
To compute the instantaneous speed and acceleration the central difference is used. For acceleration only the forward (positive) acceleration values are considered. In addition to the time spent moving per hour and the total distance, we computed various statistics of the instantaneous speed, acceleration and directional change.

### Definition directional change
For directional change the angle between two succeeding time-points is computed. The angle at time $t_i$ is defined by the locations $P_i$ of the body part selected `LOCOMOTION_NODE` (typically *Tail_1*). The angle is computed from two segments $\overline{P_{i-1}P_i}$ and $\overline{P_{i}P_{i+1}}$. The angle is 0 if the segments are parallel and in range $(-180, +180)$ degrees.

To get more robust to noise in the body part localizations, the raw yx-locations are smoothed with a Gaussian with sigma=`LOCOMOTION_SPATIAL_SIGMA` (default 1). In addition, the time can be sub-sampled using the settings parameter `LOCOMOTION_DC_SUBSAMPLE` (default 8); then only every 8th frame is considered for computing the angles. All angles are given in degrees.

## Run specifically
Result tables and plots are stored in `RESULTS_ROOT_DIR/LOCOMOTION_OUTDIR` (default: `./locomotion`)

```bash
# Generate output tables
python locomotion_analysis.py

# Basic plots per Stages and Genotypes
python locomotion_plots.py
```

## Computed features

| Feature           | Description                                                          | 
| :---------------- | :------------------------------------------------         | 
|speed_moving_mean  | mean of the instantaneous speed while moving (cm/sec)     |
|speed_moving_std   | std of the instantaneous speed while moving               |
|speed_moving_p95   | 95th percentile of the instantaneous speed while moving   |
|time_spend_moving_ratio| ratio of frames thresholded as moving and the total number of frames (au)|
|directional_change_mean| mean of the directional change (degree)               |
|directional_change_std|  std of the directional change (degree)                |
|directional_change_95|  95th percentile of the directional change (degree)     |
|directional_change_pos_mean| mean directional change regarding positive angles only | 
|directional_change_pos_std| std directional change regarding positive angles only |
|directional_change_pos_95|  95th percentile directional change regarding positive angles only |
|directional_change_neg_mean| mean directional change for regarding negative angles            |
|directional_change_neg_std| std directional change for regarding negative angles              |
|directional_change_neg_95| 95th percentile directional change for regarding negative angles   |
|acceleration_mean| mean positive acceleration            |
|acceleration_p95| 95th percentile positive acceleration  |
|total_distance| total distance traveled while moving     |

