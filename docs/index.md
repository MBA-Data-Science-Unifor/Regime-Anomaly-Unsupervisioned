# RT-IoT2022 — Regimes and Anomalies

This project is under development and analyzes IoT network traffic using the
RT-IoT2022 dataset.

## Current state

The code, documentation, artifact, and application structures are ready. The analysis,
training, evaluation, and publication of the final model have not yet been completed.

The work is organized into three notebooks:

| Order | Notebook | Purpose |
| --- | --- | --- |
| 1 | `artifacts/notebooks/01_EDA.ipynb` | exploratory analysis |
| 2 | `artifacts/notebooks/02_preprocessing.ipynb` | data preparation |
| 3 | `artifacts/notebooks/03_Modeling.ipynb` | modeling |

No metric or conclusion should be presented as final at this stage.

## Future application

The Streamlit application will consume approved artifacts from `artifacts/`, display
Plotly charts, and allow users to test the final model. The application will not train
models.

See [Project Structure](project-analysis.md) for the planned workflow.
