# Implementation

## Components

| Component | Responsibility |
| --- | --- |
| artifacts/notebooks | analysis record; notebooks 02–05 fit, evaluate and publish |
| src/regime_anomaly | reusable code shared by notebooks and inference (`preprocessing`, `modeling`, `artifacts`) |
| artifacts | locally generated publication contract |
| src/app.py | read-only presentation of published results and inference on uploaded CSV files |
| docs | methodology, evidence, decisions, and limitations |
| tests | preprocessing, model bundle, manifest, and translation checks |

## Artifact policy

Raw data, processed datasets, PNG figures, CSV tables, serialized models, and metadata
are generated locally and ignored by Git. Directory placeholders remain versioned.
`metadata/manifest.json` records the raw file's size, SHA-256 hash, UCI identifier, DOI
and license, the SHA-256 hash of every published artifact, and the reproduction steps.

Streamlit must not train or rewrite analytical artifacts. It remains usable in an
informational mode when optional artifacts are absent.

## Execution

    uv sync --locked --group analysis --group docs --group test
    uv run invoke notebooks                 # 01 to 05 in order; --start 03_Modeling to resume
    uv run regime-analysis                  # compare artifacts with the manifest
    uv run streamlit run src/app.py
    uv run invoke docs --build --strict
    uv run pytest

`regime-analysis` exits with status 1 when a registered artifact is missing or its hash
differs, so it can guard a deployment step.

## Not yet defined

Monitoring and retraining depend on the pending team review (see
[Status](status.md)): the alert rate and regime names must be confirmed before drift
thresholds or a retraining schedule make sense.
