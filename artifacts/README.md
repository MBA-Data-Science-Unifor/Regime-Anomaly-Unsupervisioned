# Generated artifacts

This directory is the publication contract between the analysis pipeline and Streamlit.

- `data/raw`: local RT-IoT2022 source file
- `data/processed`: enriched row-level results
- `tables`: presentation-ready CSV tables
- `images`: presentation-ready PNG charts
- `models`: serialized final model bundle
- `metadata`: metrics and integrity manifest

Generate everything with `uv run python -m regime_anomaly.pipeline`. The pipeline does
not download the dataset. Do not edit generated files manually.
