# Success Criteria

The final criteria will be approved before the final evaluation. This page records the
expected format without presenting targets as already validated.

## Data criteria

- documented schema and grain;
- identifier columns and labels separated from training features;
- missing, infinite, duplicate, and constant values handled explicitly;
- reproducible training, calibration, and test splits.

## Modeling criteria

- comparison of more than one approach;
- recorded seeds and parameters;
- no label leakage into unsupervised training;
- model and preprocessing serialized together;
- documented rationale for the selected model.

## Evaluation criteria

- metrics appropriate for class imbalance;
- confusion matrix and analysis by traffic type;
- evaluated threshold stability and sensitivity;
- documented limitations and failure cases.

## Delivery criteria

- reproducible artifacts under `artifacts/`;
- a Streamlit application able to read results and test the model;
- MkDocs documentation built without errors;
- passing structural and inference tests.
