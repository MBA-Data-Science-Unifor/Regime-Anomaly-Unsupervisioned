# Steel Industry Energy Consumption — Regimes and Anomalies

This project investigates operating regimes and unusual energy-consumption observations
in a South Korean steel industry dataset. The analysis is unsupervised: Load_Type
provides only the known cardinality of three regimes and is not used as an input feature
or as a training label.

## Current state

| Component | State |
| --- | --- |
| Raw dataset | available locally; excluded from Git |
| EDA | implemented and documented |
| Data dictionary | generated locally |
| Exploratory figures and tables | generated locally; excluded from Git |
| Preparation notebook | planned |
| Final model comparison | pending |
| Frozen evaluation | pending |
| Streamlit | read-only scaffold available |

The current clustering and anomaly results are exploratory evidence, not final model
selection or business validation.

## Workflow

1. understand the measurement grain and quality;
2. examine individual distributions and temporal behavior;
3. study relationships without using Load_Type;
4. project the feature space with PCA and t-SNE;
5. inspect three-regime K-Means and GMM baselines;
6. inspect Isolation Forest anomaly signals;
7. move approved decisions to preparation, modeling, and evaluation.

See [Initial Findings](initial-findings.md) for the evidence currently available.
