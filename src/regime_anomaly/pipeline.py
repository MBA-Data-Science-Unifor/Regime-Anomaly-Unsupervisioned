"""Artifact contract and integrity check (``regime-analysis``).

Training and publication happen in the notebooks; this command never fits or rewrites
anything. It creates the artifact folders and compares published files with the
SHA-256 hashes in ``metadata/manifest.json``.
"""

from __future__ import annotations

import sys
from collections import Counter

from pathlib import Path
from .data import LABEL_COLUMN, load_data
from .artifacts import MANIFEST, verify_manifest
from .config import ARTIFACTS, MODELS_DIR, PROCESSED_DIR, RAW_DIR, ensure_artifact_dirs, METADATA_DIR
from .preprocessing import FEATURE_CONFIGS, FEATURE_DELETED, FEATURE_CATEGORICAL, FEATURE_NUMERIC, FEATURE_REPORTED, split_columns, build_preprocessor
import pandas as pd
import numpy as np
import joblib
import json

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


def run_preprocessing():
    ensure_artifact_dirs()
    df = load_data()
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df = df.sort_values("date").reset_index(drop=True)

    X, y = df.drop(columns=[LABEL_COLUMN]), df[LABEL_COLUMN]
    cut = int(len(df) * 0.8)                       # split temporal 80/20
    X_train, X_test = X.iloc[:cut].copy(), X.iloc[cut:].copy()
    y_train, y_test = y.iloc[:cut].copy(), y.iloc[cut:].copy()

    SELECTED_CONFIG = "Base + Day_of_week + PCA90"

    cols, pca_variance = FEATURE_CONFIGS[SELECTED_CONFIG]
    numeric, categorical = split_columns(cols)
    pipeline = build_preprocessor(numeric, categorical, pca_variance)

    X_train_p = pipeline.fit_transform(X_train)    # fit só no treino
    X_test_p = pipeline.transform(X_test)

    np.save(PROCESSED_DIR / "x_train.npy", X_train_p)
    np.save(PROCESSED_DIR / "x_test.npy", X_test_p)
    y_train.to_csv(PROCESSED_DIR / "y_train.csv", index=False)
    y_test.to_csv(PROCESSED_DIR / "y_test.csv", index=False)
    joblib.dump(pipeline, MODELS_DIR / "preprocessor.joblib")

    RAW = Path(RAW_DIR / "Steel_industry_data.csv")

    # Definição das Features
    feature_data = {
        "raw_file": str(RAW),
        "chosen_config": SELECTED_CONFIG,
        "feature_numeric": FEATURE_NUMERIC,
        "feature_categoric": FEATURE_CATEGORICAL,
        "feature_reporting_only": FEATURE_REPORTED,
        "feature_deleted": FEATURE_DELETED,
        "target": LABEL_COLUMN,
        "chosen_config": "numeric + pca90",
        "split_strategy": "temporal_80_20",
        "n_rows_total": int(len(df)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "pca_components": [f"PC{i+1}" for i in range(X_train_p.shape[1])],
        "train_date_range": [str(X_train["date"].min()), str(X_train["date"].max())],
        "test_date_range":  [str(X_test["date"].min()),  str(X_test["date"].max())],
    }

    (METADATA_DIR / "preprocessed_data.json").write_text(
        json.dumps(feature_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


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
