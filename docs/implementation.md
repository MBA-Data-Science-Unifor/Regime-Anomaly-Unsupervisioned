# Implementation

## Components

| Component | Responsibility |
| --- | --- |
| artifacts/notebooks | investigation and experiment records |
| src/regime_anomaly | approved reusable code |
| artifacts | local generated publication contract |
| src/app.py | read-only dashboard for monitoring, alerts, models, and reports |
| docs | methodology, evidence, decisions, and limitations |
| tests | structural and future inference validation |

## Artifact policy

Raw data, processed datasets, PNG figures, CSV tables, serialized models, and metadata
are generated locally and ignored by Git. Directory placeholders remain versioned.
A future manifest will provide hashes and reproduction instructions.

Streamlit must not train or rewrite analytical artifacts. It remains usable in an
informational mode when optional artifacts are absent and reloads results published to
`data/processed/analysis_results.csv` through an explicit user action.

The dashboard presents historical results as a monitoring simulation; alerts support
operational investigation and are not fault diagnoses or maintenance predictions.

## Execution

    uv run streamlit run src/app.py
    uv run --group docs invoke docs --build --strict
    uv run --group test pytest

The deployment, monitoring, and retraining plan will be defined only after final
evaluation.
