## Analysis of straight-line movement episodes
---

Analysis of straight-line episodes is implemented in [notebook](../analysis_episodes/straight_line_episodes.ipynb)

### 1. Find straight-line movement episodes

To identify episodes in which the frogs moved approximately in a straight line, we first filtered the video frames where the frog's body-axis vector was aligned with its movement vector, indicating active forward motion. This was achieved by projecting the frog's unit displacement vectors onto its body axis, defined by the unit vector from `Tail_Stem` to `Heart_Center`. The resulting forward correlation was denoised using a median filter with a window size of 3 frames (1/20 sec) and thresholded at a **minimum correlation of 0.8**. 

Following thresholding, the candidate episodes were further refined by requiring a:

* minimum **duration of 90 frames (1.5 sec)** 
* minimum average **speed of 1.2 cm/sec**, and a 
* minimum trajectory **confinement ratio of 0.95**. 

The confinement ratio is defined as the ratio of the net, Euclidean distance traveled to the actual distance traveled along its trajectory. For visual inspection, all straight-line episodes are exported as montage movies.

### 2. Analysis of Straight-Line Movement Episodes

For each found straight-line episodes, we computed the features as described in the [analysis](../analysis/) section:

* [Basic Locomotion](../doc/locomotion.md)
* [Area explored](../doc/area_explored.md)
* [Angle ranges](../doc/angle_range.md)
* [Angle correlation](../doc/angle_correlation.md)
* [Frequency](../doc/frequency.md)

All statistics for features (such as mean, std, p95, etc) are then computed over each respective episode.
