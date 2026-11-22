"""Loading helpers for the Steel Industry Energy Consumption dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import RAW_DIR

DEFAULT_DATASET = RAW_DIR / "Steel_industry_data.csv"
LABEL_COLUMN = "Load_Type"


def load_data(path: str | Path | None = None) -> pd.DataFrame:
    """Read the local dataset without downloading or transforming its values."""
    source = Path(path) if path else DEFAULT_DATASET
    if not source.exists():
        raise FileNotFoundError(f"Base local não encontrada: {source}")
    return pd.read_csv(source, low_memory=False)
