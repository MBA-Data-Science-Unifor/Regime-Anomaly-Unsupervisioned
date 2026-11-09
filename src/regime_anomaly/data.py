"""Minimal RT-IoT2022 loading helpers for future notebooks."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .config import RAW_DIR

DEFAULT_DATASET = RAW_DIR / "RT_IOT2022"
LABEL_COLUMN = "attack_type"


def snake_case(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z]+", "_", value.strip())
    return value.strip("_").lower()


def load_data(path: str | Path | None = None) -> pd.DataFrame:
    """Read the local dataset without downloading or transforming its values."""
    source = Path(path) if path else DEFAULT_DATASET
    if not source.exists():
        raise FileNotFoundError(f"Base local não encontrada: {source}")
    frame = pd.read_csv(source, low_memory=False)
    frame.columns = [snake_case(column) for column in frame.columns]
    if frame.columns[0] == "unnamed_0":
        frame = frame.rename(columns={"unnamed_0": "record_id"})
    return frame
