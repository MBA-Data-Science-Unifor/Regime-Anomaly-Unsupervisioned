# Generated artifacts

This directory is the publication boundary between notebooks, reusable code, MkDocs,
and Streamlit.

| Path | Purpose |
| --- | --- |
| `data/raw/` | local UCI CSV; never modified by notebooks |
| `data/processed/` | generated dictionaries and future prepared datasets |
| `tables/` | generated exploratory summaries and future evaluation tables |
| `images/` | generated PNG figures |
| `models/` | future serialized preprocessing and final model |
| `metadata/` | future metrics, hashes, parameters, and manifest |

The current raw source is `data/raw/Steel_industry_data.csv`. Generated contents and
local raw data are intentionally ignored by Git; only directory placeholders are kept.
Run the notebooks or the future pipeline to reproduce them.

Do not train models from Streamlit. The application must consume approved artifacts
read-only and remain usable when optional artifacts are absent.

