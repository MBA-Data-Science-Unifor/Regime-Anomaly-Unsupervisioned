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
| Preparation | fitted, leakage-safe transformations | done; awaiting team approval |
| Modeling | reproducible comparison and stability | done |
| Evaluation | frozen metrics and external assessment | done |
| Publication | manifest, final model, application | done (model v1.1) |
| Team review | decisions, regime names, alert triage | waiting on people |

## Reflection

Three regimes are stable (bootstrap ARI 0.999) and electrically interpretable, but they
describe the plant's electrical state rather than the Load_Type tariff schedule. Regime
names, causal explanations and the alert rate still need plant and operations input.
