# Motor neuron and V1 inhibitory interneuron analysis
---

This is custom analysis code associated with the publication:

> **Multifold increase in spinal inhibitory cell types with emergence of limb movement *(Cell Reports, 2026)***
>
> Corresponding author: Lora Sweeney (lora.sweeney@ista.ac.at)

---

## Introduction
There are several kinds of locomotion and behavioral analyses implemented grouped into six categories:

* [**Basic Locomotion**](doc/locomotion.md)
* [**Area explored**](doc/area_explored.md)
* [**Angle ranges**](doc/angle_range.md)
* [**Angle correlation**](doc/angle_correlation.md)
* [**Frequency**](doc/frequency.md)
* [**PCA and Moving visualizations**](doc/pca_moving.md)

For each category there are two Python (ver. $\geq$ 3.6) scripts:

* `<category>_analysis.py`
* `<category>_plots.py`

All scripts reside in the [analysis](./analysis) folder. For convenience the entire computation can be triggered in parallel from a single [entry script](#run-analysis)

## Folder structure, settings and analysis parameters

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

## Run analysis

#### On SLURM cluster

The full analysis can be executed on a SLURM HPC cluster.

1. [SLEAP predictions](scripts/README.md#run-sleap-prediction-of-movies-on-slurm-cluster)
2. [Feature computations and plotting](scripts/README.md#run-analysis-on-slurm-cluster)

#### Locally

To run the pipeline locally for all analysis categories:

```bash
cd analysis
python analysis_run.py --settings <path-to-yaml>

# For help on other parameters use: 
python analysis_run.py --help
```

Each analysis category will run in parallel. Results are stored in `RESULTS_ROOT_DIR` set globally in the YAML settings file. It can be given as argument to `analysis_run.py`.

## Dependencies
---

The analysis depends heavily on [tadpose](https://github.com/sommerc/tadpose). The Python SLEAP package is typically not required (only for [metrics](scripts/README.md#metrics-generate-sleap-validation-metrics-as-table))

You can install all dependencies into a new environment **frog_analysis** by using the supplied [environment.yml](./environment.yaml)

```bash
conda env create -f environment.yaml
```

## Contributors
* Lora Sweeney
* Florina Alexandra Toma
* Christoph Sommer
* Robert Hauschild
* Zoe Harrington
* Mara Julseth






