# PBL Board

## What we know

- the UCI steel-industry dataset is available locally;
- it contains 35,040 quarter-hour observations and 11 columns;
- there are no missing or exact duplicate rows in the local file;
- Load_Type contains three categories;
- EDA artifacts and baselines can be reproduced locally;
- generated and heavy files are excluded from Git.

## What we are investigating

- whether three unsupervised regimes are stable and operationally interpretable;
- how calendar effects and correlated electrical variables affect segmentation;
- which extreme observations are legitimate regime behavior;
- how anomaly rankings change with assumptions and time;
- which preparation and model choices generalize beyond the EDA.

## Work plan

| Stage | Evidence | State |
| --- | --- | --- |
| EDA | dictionary, figures, tables, hypotheses | review in progress |
| Preparation | fitted, leakage-safe transformations | pending |
| Modeling | reproducible comparison and stability | pending |
| Evaluation | frozen metrics and external assessment | pending |
| Publication | manifest, final model, application | pending |

## Reflection

The current EDA supports continued investigation of three regimes, but it does not
validate class correspondence, causal explanations, or production thresholds.
