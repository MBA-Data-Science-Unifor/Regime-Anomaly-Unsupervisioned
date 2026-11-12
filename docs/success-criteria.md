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

- keep Load_Type outside training features;
- do not use supervised metrics during EDA;
- reserve external agreement measures for the frozen evaluation protocol;
- report failure cases, sensitivity, and limitations;
- distinguish exploratory findings from approved conclusions.

## Delivery

- keep generated or heavy artifacts outside Git;
- reproduce artifacts from notebooks or the future pipeline;
- build MkDocs in strict mode;
- keep Streamlit read-only with respect to training;
- maintain passing tests and an integrity manifest before final publication.
