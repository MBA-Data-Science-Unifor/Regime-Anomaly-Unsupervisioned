# Data Preparation

Data preparation will be developed in
`artifacts/notebooks/02_preprocessing.ipynb` and, once approved, extracted into
reusable functions under `src/regime_anomaly/`.

## Planned steps

- normalize column names;
- separate identifiers, features, and the external label;
- explicitly handle missing and infinite values;
- remove uninformative columns with justification;
- encode categorical features;
- transform or scale numerical features when necessary;
- create reproducible training, calibration, and test splits;
- persist preprocessing together with the model.

## Leakage prevention

`Attack_type` must not be used as a feature in unsupervised models. Any use of the label
to define a reference, calibrate a threshold, or evaluate performance must be documented
separately.

## Future outputs

Processed data will be written to `artifacts/data/processed/`. No final processed file
has been published at this stage.
