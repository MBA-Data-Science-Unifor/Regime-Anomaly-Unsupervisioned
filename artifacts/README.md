# Generated artifacts

## Production snapshot

The versioned runtime allowlist is: `data/processed/analysis_results.csv`,
`data/processed/prepared_dataset.csv`, `metadata/preprocessing.json`,
`metadata/final_metrics.json`, `metadata/manifest.json`, and
`models/final_model.joblib`. Streamlit reads this complete set; the final model also
enables the published-model integration test. Other generated files remain ignored.

This directory is the publication boundary between notebooks, reusable code, MkDocs,
and Streamlit.

| Path | Purpose |
| --- | --- |
| `data/raw/` | local UCI CSV; never modified by notebooks |
| `data/processed/` | generated data dictionary, prepared dataset, and published analysis results |
| `tables/` | generated exploratory, modeling, and review summaries |
| `images/` | generated PNG figures |
| `models/` | serialized `final_model.joblib` (`ModelBundle`) |
| `metadata/` | preprocessing metadata, final metrics, hashes, parameters, and manifest |

The current raw source is `data/raw/Steel_industry_data.csv`. Generated contents and
local raw data are intentionally ignored by Git; only directory placeholders are kept.
Run notebooks 01–04 to reproduce them. Notebook 03 is the publication step: it writes
the final model, metrics, results, and integrity manifest; notebook 04 only reviews
those approved artifacts.

Do not train models from Streamlit. The application must consume approved artifacts
read-only and remain usable when optional artifacts are absent.

