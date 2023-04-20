## Frog-Analysis scripts
---

Collection of scripts for various tasks

### Cluster prediction of movies with SLEAP
The SLURM sbatch script `predict_sleap.sh` can be used to predict `<N>` .mp4 movies organized in a folder structure below `MOVIE_ROOT` recursively. In addition, the two SLEAP models `SLEAP_CENTROID_MODEL`, `SLEAP_INSTANCE_MODEL` and the maximaum expected number of animals `MAX_ANAIMALS` is required.

**Example**
```bash
sbatch --array=0-<N-1> --time=5:00:00 predict_sleap.sh MOVIE_ROOT SLEAP_CENTROID_MODEL SLEAP_INSTANCE_MODEL MAX_ANAIMALS
```

If results files already exist, and you want to overwrite them, then add `true` as 5th argument

```bash
sbatch --array=0-<N-1> --time=5:00:00 predict_sleap.sh MOVIE_ROOT SLEAP_CENTROID_MODEL SLEAP_INSTANCE_MODEL MAX_ANAIMALS true
```

To retrieve the number <N> (if not known) use:

```
shopt -s globstar nullglob
ls MOVIE_ROOT/**/*.mp4 | wc -l
```

Important: you need to create a `logs` folder next to the script on the cluster to retrieve outputs from the SLURM array job.

### Manual annotation of the dish ROI using ImageJ/Fiji
For the calibration of pixel sizes, one needs to annotate the dish with a circle ROI. The script `create_dish_roi_semi_automatic.ijm` will create a <movie_name>.roi file located next to the movie. All movies need to be ROI-annotated.

### Output the SLEAP validation metrics as table
The script `metrics.py` outputs a table containing most important SLEAP validations metrics. Note, this scripts needs SLEAP installed in your environment.

### Mutant side switching
If an animal is handicaped on one side, we use the manual annotation of the mutant side from `mutant.tab` to create an <movie_name>.json file. This contains the information whether all processing should be done on the original movie or on a mirrored version. The mutant side should always be on the left. 

To generate these .json files, follow steps in `mutant_side_generate_from_tab.ipynb`

### Helper
The cluster script `predict_sleap.sh` genrates .slp and .h5 output. After local proofreading of .slp files the .h5 analysis file needs to be regenerated. One can use the Windows batch script `slp2h5_win.bat` for that purpose.