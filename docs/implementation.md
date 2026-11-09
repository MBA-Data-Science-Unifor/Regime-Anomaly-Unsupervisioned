# Implementation

## Components

| Component | Responsibility |
| --- | --- |
| `artifacts/notebooks/` | investigation and experiment records |
| `src/regime_anomaly/` | approved reusable code |
| `artifacts/` | publication of derived data and the model |
| `src/app.py` | presentation and model testing |
| `tests/` | structural validation and future inference validation |

## Publication contract

Streamlit is expected to consume the following paths in the future:

```text
artifacts/data/processed/
artifacts/tables/
artifacts/images/
artifacts/models/final_model.joblib
artifacts/metadata/final_metrics.json
artifacts/metadata/manifest.json
```

The application must continue to work in informational mode when these files do not
yet exist. Training and result generation are not part of the web process.

## Localization

The Streamlit interface uses Brazilian Portuguese (`pt-BR`) by default and offers
English as an alternative. Interface messages live in
`src/regime_anomaly/locales/`; code identifiers and this documentation remain in
English. The MkDocs theme controls are localized to Brazilian Portuguese without
translating the English page content.

## Execution

```bash
uv run streamlit run src/app.py
```

The deployment, monitoring, and retraining plan will be defined after the final model
is evaluated.
