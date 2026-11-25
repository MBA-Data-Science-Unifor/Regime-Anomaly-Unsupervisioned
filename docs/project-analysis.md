# Project Structure

## Workflow

    artifacts/data/raw/Steel_industry_data.csv
            ↓
    01_EDA.ipynb
            ↓
    02_Preprocessing.ipynb
            ↓
    03_Modeling.ipynb
            ↓
    artifacts/{data/processed,tables,images,models,metadata}
            ↓
    MkDocs and Streamlit

## Publication contract

| Path | Contents | Git policy |
| --- | --- | --- |
| artifacts/data/raw | local UCI source | ignored |
| artifacts/data/processed | dictionaries and prepared data | ignored |
| artifacts/tables | generated analytical tables | ignored |
| artifacts/images | generated figures | ignored |
| artifacts/models | serialized `ModelBundle` (`final_model.joblib`) | ignored |
| artifacts/metadata | metrics, preprocessing record and manifest | ignored |
| artifacts/notebooks | reproducible investigation | versioned with outputs, so results read without re-running |

Approved reusable logic should move from notebooks to src/regime_anomaly. Documentation
records stable methodology and preliminary evidence, while heavy outputs are regenerated
locally.
