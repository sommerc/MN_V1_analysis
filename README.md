# Frog Analysis
---
**work in progress**

## Analsyis
There are several kinds of locomations and behavioural analyses implemented:

* [Basic Locomotion](./locomotion.md)
* [Area explored](./area_explored.md)
* [Angle ranges](./angle_range.md)
* [Angle correlation](./angle_correlation.md)
* [Frequency](./frequency.md)
* [PCA and Moving visiualizations](./pca_moving.md)

## Folder structure, settings and analysis paramters:
---

Settings and parameters are organzied in YAML. The current pipeline is configured in [analysis_settings.yml](analysis_settings.yml). For an more minimal example template see [analysis_settings.template.yml](analysis_settings.template.yml)

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
Each .mp4 movie needs and SLEAP .h5 output and a Fiji .roi annotation.

The settings YAML file contains gerneral parameters at its root level and specific analysis parameters per `STAGE_GRP`. Hence, movies below a stage group are processed with the same parameters.


## Run 
---

To run the current pipeline type

```
cd analysis
python analyis_run.py

# For help use: 
# python analyis_run.py -h 
```

## Dependencies
---

The analysis dependes heavyly on [tadpose](https://github.com/sommerc/tadpose) and the usual scientific Python stack. The Python SLEAP package is typically not required (only for [metrics](scripts/README.md))



