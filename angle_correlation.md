
# Angle Correlation Analysis
---
## Basics
Angle Correlation features extract the correlation of angles measured at two defined body-part locations in a time resolved manner. In short, the correlation is computed as windowed Pearson correlation. From the correlation coefficient distribution (over time) several measures are extracted.

### Setup
In the settings YAML file. One needs to define the angles for which the correlation is computed, e.g the correlation of the angles at the left and right ankle.

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

In addition, parameters for the detection of *active* episodes - in which the correlation is computed - and window size for the correlation need to be given, e. g.
```yaml
  ANGLE_CORR_ACTIVE_THRESH: 0.1
  ANGLE_CORR_ACTIVE_SMOOTH: 15
  ANGLE_CORR_TEMP_ANGLE_SMOOTH: 1
  ANGLE_CORR_WIN_SIZE: 31
```

### Selection of *active* episodes
Both defined angles - A and B - for the angle correlation are first slightly smooth with a Gaussian of sigma=`ANGLE_CORR_TEMP_ANGLE_SMOOTH` using `scipy.ndimage.gaussian_filter1d` function. Then, the the *z-score* of the smoothed angles walues is computed. The z-score subtracts the mean and divides by the standard deviation to center the angle values around zero. This is required for the later frequency estimation.

To define episodes, i. e. frames, where the angles have enough variance to compute meaningful correlations, we compute the gradient magnitude of the smoothed angle z-scores using central differences `numpy.gradient`. The gradient magnitude involves a second, usually higher Gaussian smoothing of sigma=`ANGLE_CORR_ACTIVE_SMOOTH`.

The maximum over both gradient magnitudes are computed and thresholded with `ANGLE_CORR_ACTIVE_THRESH`. Only correlations from time frames exceeding this threshold are used the compute the angle correlation distribution.

### Computing the angle correlation
The correlation is computed by a centered, rolling Pearson correlation using `A.rolling(win, center=True).corr(B)` where A and B are the smoothed and z-scored input angle time courses. The resulting correlation distribution ranging $\in [-1,1]$ are visualized in `RESULTS_ROOT_DIR/ANGLE_CORR_OUTDIR/imgs`.

From the distribution characterizing correlation features are extracted (see below)


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
The median of the correlation distribution
            
### corr_p05
The 5th percentile of the correlation distribution

### corr_p95
The 95th percentile of the correlation distribution

### corr_skewness
The skewness of the correlation distribution. The skewness indicates how *skewed* a probability density distribution is. A standard normal Gaussian distribution has a skewness of zero. The more weight on the positive tail of the distrbution the smaller the skewness value gets, and vica verse. Note, this is opposite than the `corr_median`

### corr_std
The standard deviation of the correlation distribution

### computed_of_ratio
The ratio of frames which where thresholded to be *active*.