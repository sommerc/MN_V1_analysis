# MN_V1_analysis
This is custom analysis code associated with the publication:
> **Spinal cord neural diversity scales with movement complexity during frog metamorphosis**
>
> Contact Lora Sweeney (lora.sweeney@ista.ac.at)


---

## Introduction
There are several kinds of locomotion and behavioral analyses implemented grouped into six categories.

* [Basic Locomotion](doc/locomotion.md)
* [Area explored](doc/area_explored.md)
* [Angle ranges](doc/angle_range.md)
* [Angle correlation](doc/angle_correlation.md)
* [Frequency](doc/frequency.md)
* [PCA and Moving visualizations](doc/pca_moving.md)

To each category there are two Python (ver. > 3.6) scripts:
* \<category\>_analysis.py
* \<category\>_plots.py

All scripts reside in the "analysis" folder. For convenience the entire computation can be triggered in parallel from a single [entry script](#run)

## Folder structure, settings and analysis parameters:
---

Settings and parameters are organized in YAML. The current pipeline is configured in [analysis_settings.yml](analysis_settings.yml). For an more minimal example template see [analysis_settings.template.yml](analysis_settings.template.yml)

The overall input Folder structure has two levels.

Stages and genotypes. 

```bash
├── MOVIE_ROOT
│   ├── STAGE_GRP_1
│   │   ├── GENOTYPE_1
│   │   ├── GENOTYPE_2
│   │   │   ├── movie.mp4
│   │   │   ├── movie.roi
│   │   │   ├── movie.json (optional)
│   │   │   ├── movie.prediction.slp
│   │   │   ├── movie.prediction.analysis.h5
│   ├── STAGE_GRP_2
│   │   ├── GENOTYPE_1
│   │   ├── GENOTYPE_3
```
Each .mp4 movie needs and SLEAP .h5 output and a [Fiji .roi](./scripts/README.md#manual-annotation-of-the-dish-roi-using-imagejfiji) annotation.

The settings YAML file contains general parameters at its root level and specific analysis parameters per `STAGE_GRP`. Hence, movies below a stage group are processed with the same parameters.


## Run 
---

To run the pipeline for all analysis categories.

```bash
cd analysis
python analysis_run.py --settings <path-to-yaml>

# For help on other parameters use: 
python analysis_run.py --help
```

Results are stored in `RESULTS_ROOT_DIR` set globally in the YAML settings file. It can be given as argument to `analysis_run.py`.

## Dependencies
---

The analysis depends heavily on [tadpose](https://github.com/sommerc/tadpose) and the typical scientific Python stack. The Python SLEAP package is typically not required (only for [metrics](scripts/README.md))

You can install all dependencies into a new environment **frog_analysis** by using the supplied `environment.yml`

```bash
conda env create -f environment.yaml
```

## Contributors
---
Lora Sweeney
Florina Toma
Mara Julseth
Alexia Wilson
Zoe Harrington




