# EAF PCC Source Dataset

This repository organizes the source-domain data used for physics-enhanced electric arc furnace time-series modeling. Measurements originate from Ugwuagbo et al. (2021). Repository maintainer: Tong Wu. [中文说明](README.md).

## Contents

- `data/raw/supplementary_exports/`: four locally retained CSV exports of the published supplementary measurements, preserved byte for byte. These semicolon-delimited exports can contain multiple blocks or repeated headers. They are not asserted to be a byte-identical mirror of the publisher's Excel workbook.
- `data/selected_local/`: the four historical `02.` input files, also byte-preserved. The THD file contains additional time periods. The common timestamp intersection defines the study window.
- `data/processed/pcc_measurements_aligned.csv`: measurement-only common-time table, 1140 rows and 148 columns. Numeric strings are retained, columns are prefixed by source table, and no interpolation is performed.
- `data/processed/data1_physical_model_dataset.csv`: saved 1140-row, 77-column wide table containing measurements, equivalent-model features and residuals.
- `data/processed/data1_gru_phase_sequence.csv`: saved 3420-row, 22-column phase sequence table, with six principal dynamic features and power-residual labels.
- `metadata/`: file hashes, field dictionary and split boundaries. `checksums.sha256` covers every packaged file except itself.

The aligned observation window runs from 2018-11-22 20:01:00 through 2018-11-23 15:00:00 at 60-second intervals. The source exports do not specify a timezone, and no timezone conversion is made. Each of L1, L2 and L3 has 1140 records. There are 1140 observation times, not 3420 independent times. Chronological Train / Validation / Test splits contain 798 / 171 / 171 times or 2394 / 513 / 513 phase rows. All three phases at one time share the same split.

The selected current export contains harmonic orders 2-16 and the selected voltage export orders 2-25. The historical filename suffix `1-50` does not establish full harmonic coverage in a selected file. The larger locally retained exports are separately preserved in `raw/`.

These measurements are minute-scale PCC statistics, not instantaneous arc-terminal waveforms. Historical `CassieMayr` field names describe derived equivalent-model features rather than directly observed fast arc states. Residual targets equal `Reference_RealActivePower_kW - Feature_CassieMayrPower_kW`. Initial interval/lag values remain NaN, as recorded in the manifest. The saved derived arrays support the existing same-node correction task. Strict forecasting requires separate causal checks for derivative construction, windows, calibration and normalization. The contemporaneous reference active power must not be used to predict its own residual.

## Verification

```bash
python tools/verify_dataset.py
```

The standard-library script checks hashes, timestamps, phase rows, splits, residual identities and measured power consistency. No simulations, fitting, interpolation or training are run. Existing derived data and source exports are byte-preserved.

## Attribution

Emenike Ugwuagbo, Adeola Balogun, Ayobami Olajube, Osita Omeje, Ayokunle Awelewa, and Shehu Abba-Aliyu (2021). Experimental data on power quality assessment at point of common coupling of a steel mill to an electric power grid. *Data in Brief*, 39, 107681. https://doi.org/10.1016/j.dib.2021.107681

The source article states CC BY 4.0. Original authorship is retained and changes are identified in the manifest. See [data licensing](DATA_LICENSE.md) and [citation metadata](CITATION.cff). This repository contains source-domain data only. Target-device data, model weights, prediction outputs and manuscript documents are outside its scope.
