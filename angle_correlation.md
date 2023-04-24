
# Angle Correlation Analysis
---
## Basics
Angle Correlation features extract the correlation of angles measured at two defined body-part locations. In short, the correlation is computed as windowed Pearson correlation. From the distribution (over time) of this correlation several measures are extracted.

### Setup
In the settings YAML file. One needs to define the angle correlation is computed for, e.g the correlation of the angles at the left and right ankle.

```yaml
  ANGLE_CORR_FOR:
    LR_ankle:
      - - Left_Knee
        - Left_Ankle  # <- Angle A
        - Left_Foot   #      |
      - - Right_Knee  #      |
        - Right_Ankle # <- Angle B
        - Right_Foot
```
Note, that the name `LR_ankle` will appear in results table columns and plots. One can define as many such entries as needed.

In addition, parameters for the detection of *active* episodes and window size for the correlation need to be given, e. g.
```yaml
  ANGLE_CORR_ACTIVE_THRESH: 0.1
  ANGLE_CORR_ACTIVE_SMOOTH: 15
  ANGLE_CORR_TEMP_ANGLE_SMOOTH: 1
  ANGLE_CORR_WIN_SIZE: 31
```

### Selection of *active* episodes
Both defined angles - A and B - for the angle correlation are first slightly smooth with a Gaussian of sigma=`ANGLE_CORR_TEMP_ANGLE_SMOOTH` using `scipy.ndimage.gaussian_filter1d` function. Then, the the *z-score* of the smoothed angles is computed.

To define episodes where the angles have enough variance to compute meaningful correlations, we compute the gradient magnitude of the smoothed angle z-scores. The gradient magnitude involves a second, usually higher Gaussian smoothing of sigma=`ANGLE_CORR_ACTIVE_SMOOTH`.

The maximum over both gradient mangitudes is computed and thresholded with `ANGLE_CORR_ACTIVE_THRESH`. Onlyu correlations from times exceeding this threshold are used the compute the angle correlation.

### Computing the angle correlation




## Run specifically with default `analysis_settings.yml`:
Result tables and plots are stored in `RESULTS_ROOT_DIR/ANGLE_CORR_OUTDIR` (default: ./resutls/angle_correlation)
```
# Generate output tables
python angle_correlation_analysis.py

# Basic plots per Stages and Genotypes
python angle_correlation_plots.py
```

## Computed features

### corr_median
            
### corr_p05

### corr_p95

### corr_skewness

### corr_std

### computed_of_ratio