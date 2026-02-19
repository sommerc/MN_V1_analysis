# Additional scripts 
---

## Run analysis on SLURM HPC cluster 

First check the *settings.yaml* file to contain correct paths for inputs and results. Make sure you have conda installed and an environment called `frog_analysis`. Then

```bash
sbatch submit_analysis.sh <settings.yaml>
```

will run the entire analysis and plots. Results will be saved to the result folder specified in the *settings.yaml*.

To run only a subset of analyses, use:

```bash
sbatch --array=<i> submit_analysis.sh <settings.yaml>
```

where <i> can be chosen from:

0. Frequency
1. Locomotion
2. PCA + moving plots 
3. Area explored
4. Angle correlation 
5. Angle range

or, mix using *comma*. For instance, `--array=2,4` would submit PCA and angle correlation analysis to the cluster.


## Run SLEAP inference on new movies on SLURM HPC cluster

The SLURM sbatch script `predict_sleap.sh` can be used to predict `N` .mp4 movies organized in a folder structure below `MOVIE_ROOT` recursively. In addition, the two SLEAP models `SLEAP_CENTROID_MODEL`, `SLEAP_INSTANCE_MODEL` and the maximum expected number of animals `MAX_ANIMALS` is required.

#### Example

```bash
sbatch --array=0-<N-1> --time=5:00:00 predict_sleap.sh MOVIE_ROOT SLEAP_CENTROID_MODEL SLEAP_INSTANCE_MODEL MAX_ANIMALS
```

If result files already exist, and you want to overwrite them, then add `true` as 5th argument.

```bash
sbatch --array=0-<N-1> --time=5:00:00 predict_sleap.sh MOVIE_ROOT SLEAP_CENTROID_MODEL SLEAP_INSTANCE_MODEL MAX_ANIMALS true
```

To retrieve the number of movies below `MOVIE_ROOT` use:

```bash
shopt -s globstar nullglob
ls MOVIE_ROOT/**/*.mp4 | wc -l
```

**Important**: you need to create a `logs` folder located next to the script on the cluster to retrieve outputs from the SLURM HPC array job.

## Manual annotation of the dish ROI using ImageJ/Fiji

For the calibration of pixel sizes, one needs to annotate the dish with a circular ROI. The script [create_dish_roi_semi_automatic.ijm](./create_dish_roi_semi_automatic.ijm) will create a `<movie_name>.roi` file located in the same folder as the movie `movie_name.mp4`. All movies need to be ROI-annotated.

## Metrics: generate SLEAP validation metrics as table

The script [metrics.py](./metrics.py) outputs a table containing most important SLEAP validations metrics. Note, this scripts needs SLEAP installed in your environment.

## Mutant side switching

If the animal is mutant on only one side of the body, use the manual annotation of the mutant side from [mutant_side.tab](./mutant_side.tab) to create a `<movie_name>.json`  file. The mutant side table contains the information to process the original or mirrored movie. The movie will be mirrored having the mutant side always on the left. 

To generate these .json files, use the script [mutant_side_run.py](./mutant_side_run.py).

```bash
python mutant_side_run.py <root-folder-of-movies> <mutant_side.tab>
```

## Helper
The cluster script `predict_sleap.sh` generates .slp and .h5 output. After local proofreading of .slp files the .h5 analysis file needs to be regenerated. One can use the Windows batch script [slp2h5_win.bat](./slp2h5_win.bat) for that purpose.