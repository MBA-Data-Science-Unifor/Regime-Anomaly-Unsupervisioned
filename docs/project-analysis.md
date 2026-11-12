# Project Structure

## Workflow

    artifacts/data/raw/Steel_industry_data.csv
            ↓
    01_EDA.ipynb
            ↓
    02_preprocessing.ipynb
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
| artifacts/models | future serialized bundles | ignored |
| artifacts/metadata | future metrics and manifest | ignored |
| artifacts/notebooks | reproducible investigation | versioned without outputs |

Approved reusable logic should move from notebooks to src/regime_anomaly. Documentation
records stable methodology and preliminary evidence, while heavy outputs are regenerated
locally.
