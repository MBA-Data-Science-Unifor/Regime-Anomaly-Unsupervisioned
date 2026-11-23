# Data Preparation

Preparation is implemented experimentally in `artifacts/notebooks/02_preprocessing.ipynb`.
Reusable operations are exposed by `src/regime_anomaly/preprocessing.py`; the final
feature selection is still under review.

## Implemented pipeline

1. parse date with day-first semantics;
2. preserve a raw immutable copy;
3. separate date, Load_Type, numerical features, and calendar categories;
4. derive approved temporal features without leaking future information;
5. standardize numerical features;
6. one-hot encode WeekStatus and Day_of_week;
7. fit every transformation on the appropriate training period only;
8. serialize preprocessing with the selected model.

The score comparison used during this experimental selection is published in
[Initial Findings](initial-findings.md) and can be regenerated from the stored notebook
output with `python scripts/generate_docs_figures.py`.

## Leakage boundary

Load_Type is not a training feature. Its cardinality defines the current three-regime
hypothesis, while its values remain reserved for later external assessment. Time-aware
splits are preferred over random-only splits because adjacent 15-minute observations are
not independent.

## Decisions still open

- treatment of skewed variables and extreme values;
- whether NSM remains numeric or becomes cyclical sine/cosine features;
- redundancy handling for highly associated electrical variables;
- feature sets for regime and anomaly tasks;
- calibration strategy for anomaly thresholds.
