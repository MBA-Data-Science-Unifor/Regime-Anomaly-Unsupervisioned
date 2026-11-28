# PBL Board

The [Problem Canvas](problem-canvas.md) answers the 11 questions on business, data,
success criteria and expected actions. This board tracks evidence and open work.

## What we know

- the UCI steel-industry dataset is available locally;
- it contains 35,040 quarter-hour observations and 11 columns;
- there are no missing or exact duplicate rows in the local file;
- Load_Type contains three categories;
- EDA artifacts and baselines can be reproduced locally;
- the raw CSV is tracked; generated artifacts are excluded from Git;
- notebook 03 contains a separate supervised `Load_Type` comparison.

## What we are investigating

- whether three unsupervised regimes are stable and operationally interpretable;
- how calendar effects and correlated electrical variables affect segmentation;
- which extreme observations are legitimate regime behavior;
- how anomaly rankings change with assumptions and time;
- which preparation and model choices generalize beyond the EDA;
- which alerts and non-alert readings are useful to operations;
- how to agree on a usefulness target, deadline and sampling plan for a pilot.

## Work plan

| Stage | Evidence | State |
| --- | --- | --- |
| EDA | dictionary, figures, tables, hypotheses | review in progress |
| Preparation | fitted, leakage-safe transformations | done; awaiting team approval |
| Modeling | reproducible comparison and stability | done |
| Historical evaluation | internal metrics, external agreement and retrospective test | complete with limitations; later independent period pending |
| Publication | manifest, final model, application | done (model v1.1) |
| Team review | decisions, regime names, alert triage | waiting on people |

## Reflection

Three regimes are stable (bootstrap ARI 0.999) and electrically interpretable, but they
describe the plant's electrical state rather than the Load_Type tariff schedule. Regime
names, causal explanations and the alert rate still need plant and operations input.

## Pending decisions and evidence

1. Confirm users, decision makers, the business objective and official track name.
2. Agree on usefulness criteria, timeline, costs and sampling before a pilot.
3. Obtain assessments for alerts and a sample of non-alerts; decide whether the
   transition filter should remain enabled.
4. Evaluate previously fixed decisions and thresholds on a later independent period.
