
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

We use the complex valued Morlet (aka Gabor) wavelet function for frequency estimation. The complex Morlet (aka Gabor) wavelet ("cmorB-C" with floating point values B, C) is given by:

$$\psi(t) = \frac{1}{\sqrt{\pi B}} \exp^{-\frac{t^2}{B}} \exp^{\mathrm{j} 2\pi C t}$$

where $B$ is the bandwidth and $C$ is the center frequency.

In addition, settings for each `STAGE_GRP` need to be defined.

```python
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
All angles are preprocessed by slightly smoothing with a Gaussian with sigma=`FREQ_TEMP_ANGLE_SMOOTH`, followed by computing the z-score.

The preprocessed angle values defined in `FREQ_FOR` are first smoothed with a Gaussian of sigma=`FREQ_ACTIVE_SMOOTH` using `scipy.ndimage.gaussian_filter1d` function. Then, the gradient magnitude is computed using central differences with `numpy.gradient`. The resulting magnitude is thresholded with `FREQ_ACTIVE_THRESH`. Only frequency estimates (mean power spectral density) from time frames exceeding this threshold are used the compute the mean PSD distribution.

### Converting frequency bins to wavelet *scales*
The continuous wavelet transform requires *scaling* factors. Scaling factors are inversely proportional to frequency. We use the PyWavelet function `pywt.scale2frequency()` to define scales corresponding to the used frequency bins. 

### Computing the power spectral density
First the coefficients of the continuous wavelet transform are computed by:

```python
pywt.cwt(
        ang_zscore,
        scales,
        wavelet,
        sampling_period=1/fps,
        method="fft",
    )
```

To obtain the power spectral density (PSD) we build the magnitude of the coefficients multiplied by their complex conjugate.

Now, the time-resolved PSD is averaged in *active* frames as described above.

### Dominant frequency
Peak finding on the mean power spectral density is applied using the function `scipy.signal.find_peaks` to obtain the dominant frequency bin. The dominant frequency hence corresponds to a local maxima in the mean power spectral density (PSD).

The prominence of a peak at the dominant frequency bin measures how much a peak *stands out* from the surrounding baseline of the signal and is defined as the vertical distance between the peak and its lowest contour line.

The analysis is repeated for frequency ranges below and a above a manual set frequency threshold $X% given by `FREQ_DOMINANT_SPLIT` (default 4.5)


### Background subtraction
In order to remove spurious low frequency content, we additionally apply background subtraction to the smoothed angle z-scores. The background is estimated by smoothing the signal with a Gaussian of sigma=`FREQ_ACTIVE_SMOOTH`.

Background subtracted results are indicated by the string *"_bs"* in the result tables.

## Run specifically
Result tables and plots are stored in `RESULTS_ROOT_DIR/FREQUENCY_OUTDIR` (default: ./frequency)

```bash
# Generate output tables
python frequency_analysis.py

# Basic plots per Stages and Genotypes
python frequency_plots.py
```

## Computed features




| Feature                   | Description                                                          | 
| :----------------         | :------------------------------------------------         | 
|dominant_freq              | dominant frequency:  local maximum frequency bin of the mean PSD. |
|dominant_freq_prominence   | prominence of the dominant frequency peak |
|dominant_freq_power        | mean power spectral density in active episodes at the *dominant_freq* |
|dominant_freq_X-              | same as above but regarding frequency values $\leq$ `FREQ_DOMINANT_SPLIT` |
|dominant_freq_prominence_X-   | same as above but regarding frequency values $\leq$ `FREQ_DOMINANT_SPLIT` |
|dominant_freq_power_X-        | same as above but regarding frequency values $\leq$ `FREQ_DOMINANT_SPLIT` |
|dominant_freq_X+              | same as above but regarding frequency values $>$ `FREQ_DOMINANT_SPLIT` |
|dominant_freq_prominence_X+   | same as above but regarding frequency values $>$ `FREQ_DOMINANT_SPLIT` |
|dominant_freq_power_X+        | same as above but regarding frequency values $>$ `FREQ_DOMINANT_SPLIT` |
|freq_active_ratio| ratio of frames which where thresholded to be *active*.| 


