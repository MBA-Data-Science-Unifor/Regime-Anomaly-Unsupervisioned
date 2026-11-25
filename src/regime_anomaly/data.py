"""Loading helpers for the Steel Industry Energy Consumption dataset."""

from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
import pandas as pd

from .config import ARTIFACTS, MODELS_DIR, RAW_DIR, PREPROCESSING_PATH

DEFAULT_DATASET = RAW_DIR / "Steel_industry_data.csv"
LABEL_COLUMN = "Load_Type"
DEFAULT_PREPROCESSOR = MODELS_DIR / "preprocessor.joblib"


def load_data(path: str | Path | None = None) -> pd.DataFrame:
    """Read the local dataset without downloading or transforming its values."""
    source = Path(path) if path else DEFAULT_DATASET
    if not source.exists():
        raise FileNotFoundError(f"Base local não encontrada: {source}")
    return pd.read_csv(source, low_memory=False)


def load_preprocessor(path_file: Path = Path(DEFAULT_PREPROCESSOR)):
    if not path_file.exists():
        raise FileNotFoundError(f"Base local não encontrada: {path_file}")

    return joblib.load(path_file)


def load_preprocessing_data():
    if not PREPROCESSING_PATH.exists():
        return {}
    return json.loads(PREPROCESSING_PATH.read_text(encoding="utf-8"))


def snake_case(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z]+", "_", value.strip())
    return value.strip("_").lower()
