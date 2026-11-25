# Steel Industry Energy Consumption — Regimes and Anomalies

This project investigates operating regimes and unusual energy-consumption observations
in a South Korean steel industry dataset. The analysis is unsupervised: Load_Type
provides only the known cardinality of three regimes and is not used as an input feature
or as a training label. A future supervised Load_Type classifier is a separate,
complementary task.

## Current state

| Component | State |
| --- | --- |
| Raw dataset | available locally; excluded from Git |
| EDA | implemented and documented |
| Data dictionary | generated locally |
| Exploratory figures and tables | generated locally; excluded from Git |
| Preparation notebooks | implemented (02 and 02b); decisions pending team approval |
| Final model comparison | complete: K-Means, three regimes, electrical features only |
| Frozen evaluation | complete on November–December |
| Anomaly detector | Isolation Forest with transition filter (model v1.1) |
| Streamlit | monitoring dashboard on published results; runs the model on uploaded CSV files |

The model is selected and evaluated, but not yet validated by the business: regime
names, the alert rate and the alerts themselves await plant and operations review (see
[Team Review](team-review.md) and [Status](status.md)).

## Workflow

1. understand the measurement grain and quality;
2. examine individual distributions and temporal behavior;
3. study relationships without using Load_Type;
4. project the feature space with PCA and t-SNE;
5. inspect three-regime K-Means and GMM baselines;
6. inspect Isolation Forest anomaly signals and their operating context;
7. compare a global baseline with contextual detection;
8. move approved decisions to preparation, modeling, and evaluation.

See [Initial Findings](initial-findings.md) for the exploratory evidence,
[Modeling](modeling.md) and [Evaluation](evaluation.md) for the final results.
See [Technical References](references.md) for the libraries, APIs, and official sources.
