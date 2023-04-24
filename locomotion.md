# Locomotion features
---
## Basics
Locomotion features extract information about the basic movement of an SLEAP-tracked body-part. Due to noise in the images, SLEAP body-part locations may exhibit dislocations of up-to few pixels. To make the locomotion analysis robust custom pre-processing is applied. The parameters of the pre-processing steps can be set in the settings YAML file.

### Definition of *moving* vs. *not-moving* episodes
To partition the time-course of an tracked animal into *moving* and *not-moving*, we first extract the yx-locations of the chosen body part from the SLEAP analysis HDF5 file. If the body part was not detected in all frames, we interpolate the missing frames using `numpy.interp`. Next, we apply a Gaussian smoothing to the y and x body-part locations using `skimage.filters.gaussian`, with the sigma set to `LOCOMOTION_SPATIAL_SIGMA` (default 1). The resulting smoothed locations are used to compute the instantaneous speed by central differences with `numpy.gradient`. We then smooth the resulting speed with a Gaussian with sigma=`LOCOMOTION_TEMPORAL_SIGMA` (default 30). Each frame is associated with a speed in pixels per frame, which we calibrate to cm per frame using the known diameter of the dish (14 cm). Finally, we threshold the calibrated speed by `LOCOMOTION_MOVING_THRESH` (default 0.02 cm/frame) to obtain a binary, frame-wise moving classification.

### Definition directional change
For directional change the angle between two succeeding time-points is computed. The angle at time $t_i$ is defined by the locations $P_i$ of the body part selected `LOCOMOTION_NODE` (typically *Tail_1*). The angle is computed from two segments $\overline{P_{i-1}P_i}$ and $\overline{P_{i}P_{i+1}}$. The angle is 0 if the segments are parallel and in range $(-\pi, +\pi)$.

To get more robust to noise in the body part localizations, the raw yx-locations are smoothed with a Gaussian with sigma=`LOCOMOTION_SPATIAL_SIGMA` (default 1). In addition, the time can be sub-sampled using the settings parameter `LOCOMOTION_DC_SUBSAMPLE` (default 8); then only every 8th frame is considered for computing the angles. All angles are given in radians. In the plots angle degrees are shown.

## Run specifically with default `analysis_settings.yml`:
Result tables and plots are stored in `RESULTS_ROOT_DIR/LOCOMOTION_OUTDIR` (default: ./locomotion)
```
# Generate output tables
python locomotion_analysis.py

# Basic plots per Stages and Genotypes
python locomotion_plots.py
```

## Computed features

### speed_mean
The mean of the instantaneous speed in cm/frame (computed as explained above)

### speed_std
The standard deviation of the instantaneous speed in cm/frame (computed as explained above)

### speed_moving_mean
The mean of the instantaneous speed in cm/frame computed only on moving frames 

### time_spend_moving
The ratio of frames thresholded as moving and the total number of frames

### directional_change_mean
The mean of the directional change angles

### directional_change_std
The standard deviation of the directional change angles

### directional_change_95
The 95th percentile of the directional change angles