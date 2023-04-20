
# Frequency Analysis
---
## Basics
Frequency features extract information about frequency of angle changes at specified body-part segments.

### More to come

## Run specifically with default `analysis_settings.yml`:
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