
# PCA and Moving Episode Visualization
---
## Basics
To visualize typical configuration of body-part skeletons the their variance we employ unsupervised dimensionality reduction. Principal component analysis (PCA) can be used to find a linear transformation in which the variance of the data points projected to its first dimension is maximized. The values of the projected data points to the first dimension (after applying the transformation) are denoted as $PC_0$. The value of $PC_0$ is used to color-code randomly sampled, aligned body-part skeletons.

As data points serve the x and y location of a sequence of aligned body-parts. The body-part sequence can be defined in the settings YAML.

Prior to computing the PCA the body-parts are ego-centrically aligned. In short, this alignment first centers the raw location to a given body-part, and then rotates the remaining body-parts that a second given body-parts always points up.

### Setup and settings
For each `STAGE_GRP` the alignment body-parts and the body-part sequence for the PCA needs to be defined, as for instance:

```
  ALIGN_CENTRAL: "Tail_1"
  ALIGN_TOP: "Heart_Center"

  PCA_PARTS:
    Tail:
      - Heart_Center
      - Tail_Stem
      - Tail_1
      - Tail_2
      - Tail_Tip
    <...>
```

The PCA visualization additionally require two parameters which are used for all `STAGE_GRP`.

```
PCA_FIT_ON_N: 8000
PCA_PLOT_N: 256
```

The PCA transformation if estimated from `PCA_FIT_ON_N` randomly selected time time frames. We use the class `sklearn.decomposition.PCA` for obtaining the PC transformation. For `PCA_PLOT_N` randomly selected body-parts skeletons, we color-code each body-part skeleton with the value of its transormed $PC_0$.

### Moving episodes visualization
In addition, moving episodes as defined in [basic locomotion](./locomotion.md#definition-of-moving-vs-not-moving-episodes) are visualized for a randomly selected time span of length given as `MOVING_PLOT_TIME_SPAN_MIN: 15`.

## Run specifically
Resulting plots are stored in `RESULTS_ROOT_DIR/PCA_OUTDIR` (default: ./resutls/pca_moving)
```
# Basic plots per Stages and Genotypes
python pca_moving_plots.py
```

## Computed features
None. Only visualizations