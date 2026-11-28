# Success Criteria

## Data

- document 11 fields, units, roles, and observed domains;
- preserve the raw CSV unchanged;
- verify missing values, duplicates, types, frequency, and time coverage;
- make preparation reproducible and leakage-safe.

## Unsupervised modeling

- use exactly three groups for the primary regime hypothesis;
- record seeds, preprocessing, features, and parameters;
- compare at least two compatible clustering geometries;
- assess compactness, separation, stability, and temporal behavior;
- treat anomaly contamination and thresholds as explicit assumptions.

## Evaluation

- keep Load_Type outside model input features; supervised training uses it as a label
  and external evaluation uses it as a reference;
- do not use supervised metrics during EDA;
- report external agreement without training the cluster models on the labels, and
  acknowledge that the historical test is not fully independent;
- report alerts and limitations; fault recall requires labels that are not available;
- distinguish exploratory findings from approved conclusions.

## Delivery

- keep generated or heavy artifacts outside Git;
- reproduce artifacts from the notebooks (`uv run invoke notebooks`) and check them with
  `uv run regime-analysis`;
- build MkDocs in strict mode;
- keep Streamlit read-only with respect to training;
- maintain passing tests and an integrity manifest before final publication.

Selection thresholds and proposed business criteria are in the
[PBL Canvas](pbl/problem-canvas.md). Business and alert-usefulness targets are not yet approved.
