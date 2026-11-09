"""Strict read-only access to the artifact contract consumed by Streamlit."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from .config import ARTIFACTS


class ArtifactStore:
    def __init__(self, root: Path = ARTIFACTS) -> None:
        self.root = root

    def _required(self, relative: str) -> Path:
        path = self.root / relative
        if not path.exists():
            raise FileNotFoundError(
                f"Artefato ausente: {path}. Publique-o pelo notebook 05."
            )
        return path

    def metrics(self) -> dict[str, object]:
        return json.loads(self._required("metadata/final_metrics.json").read_text(encoding="utf-8"))

    def table(self, name: str) -> pd.DataFrame:
        return pd.read_csv(self._required(f"tables/{name}.csv"))

    def results(self) -> pd.DataFrame:
        return pd.read_csv(self._required("data/processed/analysis_results.csv"))

    def image(self, name: str) -> Path:
        return self._required(f"images/{name}.png")

    def model(self):
        return joblib.load(self._required("models/final_model.joblib"))
