"""Artifact contract and integrity check (``regime-analysis``).

Training and publication happen in the notebooks; this command never fits or rewrites
anything. It creates the artifact folders and compares published files with the
SHA-256 hashes in ``metadata/manifest.json``.
"""

from __future__ import annotations

import sys
from collections import Counter

from .artifacts import MANIFEST, verify_manifest
from .config import ARTIFACTS, ensure_artifact_dirs

ARTIFACT_CONTRACT = {
    "raw_data": "data/raw/Steel_industry_data.csv",
    "prepared_data": "data/processed/prepared_dataset.csv",
    "processed_data": "data/processed/analysis_results.csv",
    "model": "models/final_model.joblib",
    "metrics": "metadata/final_metrics.json",
    "preprocessing": "metadata/preprocessing.json",
    "manifest": "metadata/manifest.json",
    "tables": "tables/*.csv",
    "images": "images/*.png",
    "preprocessor_data": "metadata/preprocessed_data.json",
    "preprocessor": "models/preprocessor.joblib",
}


def main() -> int:
    """Print the integrity status of published artifacts; exit 1 if any differs."""
    ensure_artifact_dirs()
    print(f"Artefatos em: {ARTIFACTS}")
    if not (ARTIFACTS / MANIFEST).exists():
        print("Manifesto ausente: execute os notebooks 01 a 05 para publicar os artefatos.")
        return 0
    status = verify_manifest(ARTIFACTS)
    for relative, state in status.items():
        if state != "ok":
            print(f"  {state:<15} {relative}")
    counts = Counter(status.values())
    print(", ".join(f"{state}: {count}" for state, count in sorted(counts.items())))
    problems = counts["alterado"] + counts["ausente"]
    if problems:
        print("Artefatos divergem do manifesto: reexecute os notebooks 03 a 05.")
        return 1
    print("Todos os artefatos registrados conferem com o manifesto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
