# Project Structure

## Planned workflow

```text
artifacts/data/raw/RT_IOT2022
        ↓
01_EDA.ipynb
        ↓
02_preprocessing.ipynb
        ↓
03_Modeling.ipynb
        ↓
artifacts/{data/processed,tables,images,models,metadata}
        ↓
src/app.py
```

The notebooks remain under `artifacts/notebooks/`. Approved code that needs to be
reused should move to `src/regime_anomaly/`.

## Future artifact contract

| Path | Contents |
| --- | --- |
| `artifacts/data/processed/` | prepared data and row-level results |
| `artifacts/tables/` | tables consumed by the documentation and Streamlit |
| `artifacts/images/` | static analysis images |
| `artifacts/models/` | serialized final model and preprocessing |
| `artifacts/metadata/` | metrics, version, and integrity manifest |

These directories are reserved. Their contents will be defined only after the three
notebooks are executed and reviewed.

## Pending documentation

The change history and detailed contribution attribution will be added later. This
version documents only the structure and current development state.
