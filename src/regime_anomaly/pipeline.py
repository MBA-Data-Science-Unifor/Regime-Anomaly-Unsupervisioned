"""Artifact publication scaffold; modelling will be implemented after the notebooks."""

from __future__ import annotations

import json

from .config import ARTIFACTS, ensure_artifact_dirs

ARTIFACT_CONTRACT = {
    "raw_data": "data/raw/Steel_industry_data.csv",
    "processed_data": "data/processed/analysis_results.csv",
    "model": "models/final_model.joblib",
    "metrics": "metadata/final_metrics.json",
    "manifest": "metadata/manifest.json",
    "tables": "tables/*.csv",
    "images": "images/*.png",
}


def main() -> None:
    """Create directories and show the future publication contract without training."""
    ensure_artifact_dirs()
    print(f"Estrutura preparada em: {ARTIFACTS}")
    print(json.dumps(ARTIFACT_CONTRACT, ensure_ascii=False, indent=2))
    print("Nenhuma análise ou modelagem foi executada.")


if __name__ == "__main__":
    main()
