
# Frequency Analysis
---
## Basics
Frequency features extract information about frequency of angle changes at specified body-part segments.

### Setup and settings
The frequency is estimated using continuous Wavlet transfrom using the python modue [PyWavelets](https://pywavelets.readthedocs.io/en/latest/). Frequency bins are chosen in the range $(0, 30] Hz$. Where 30 Hz is the Nyquist limit for the recordings with a frame rate of 60 Hz.

In the settings YAML file the the number of bins in $(0, 30] Hz$ and the mother wavelet function can be defined.

```
FREQUENCY_N: 24
FREQUENCY_WAVELET: cmorl1.5-1.0
```

We use the complex valued Morlet (aka Gabor) wavelet function for frequency estimation. The complex Morlet wavelet ("cmorB-C" with floating point values B, C) is given by:

$\psi(t) = \frac{1}{\sqrt{\pi B}} \exp^{-\frac{t^2}{B}}
          \exp^{\mathrm{j} 2\pi C t}$

where $B$ is the bandwidth and $C$ is the center frequency.

In addition, settings for each `STAGE_GRP` need to be defined.

```
  FREQ_ACTIVE_THRESH: 0.1
  FREQ_ACTIVE_SMOOTH: 15
  FREQ_TEMP_ANGLE_SMOOTH: 0.1

  FREQ_FOR:
    tail_2:
      - Tail_1
      - Tail_2 # <- Angle here
      - Tail_3
    <...>
```

where `FREQ_FOR` defines for which body-part locations the angle frequencies are estimated. The other parameters are used for preprocessing the angles values on the selection of *active* episodes.



### Selection of *active* episodes
The defined angle values defined in `FREQ_FOR` are first smoothed with a Gaussian of sigma=`FREQ_ACTIVE_SMOOTH` using `scipy.ndimage.gaussian_filter1d` function. Then, the gradient magnitude is computed using central differences with `numpy.gradient`. The resulting magnitude is thresholded with `FREQ_ACTIVE_THRESH`. Only frequency estimates from time frames exceeding this threshold are used the compute the power spectral desity distribution.

### Computing the power spectral density
The correlation is computed by a centered, rolling Pearson correlation using `A.rolling(win, center=True).corr(B)` where A and B are the smoothed and z-scored input angle time courses. The resulting correlation distribution ranging $\in [-1,1]$ are visualized in `RESULTS_ROOT_DIR/ANGLE_CORR_OUTDIR/imgs`.

### Background subtraction

## Run specifically
Result tables and plots are stored in `RESULTS_ROOT_DIR/FREQUENCY_OUTDIR` (default: ./resutls/frequency)
```
# Generate output tables
python frequency_analysis.py

# Basic plots per Stages and Genotypes
python frequency_plots.py
```

## Computed features
### dominant_freq
            
### dominant_freq_prominence

### freq_active_ratio

### Power spectral density for frequency bins in range $(0,30]$ Hz