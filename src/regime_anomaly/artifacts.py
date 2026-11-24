"""Artifact contract: read-only access for Streamlit and the integrity manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd

from .config import ARTIFACTS

MANIFEST = "metadata/manifest.json"
MANIFEST_PATTERNS = (
    "data/processed/*.csv",
    "models/*.joblib",
    "metadata/*.json",
    "tables/*.csv",
    "images/*.png",
)
REPRODUCTION_STEPS = [
    "uv sync --locked --group analysis --group docs",
    "uv run invoke notebooks  # executa 01_EDA a 05_Transition_Filter em ordem",
    "uv run regime-analysis  # confere os artefatos contra este manifesto",
]
RAW_SOURCE = {
    "origem": "UCI Machine Learning Repository, dataset 851",
    "url": "https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption",
    "doi": "10.24432/C52G8C",
    "licenca": "CC BY 4.0",
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _published(root: Path) -> list[Path]:
    target = root / MANIFEST
    return sorted(
        path for pattern in MANIFEST_PATTERNS for path in root.glob(pattern) if path != target
    )


def write_manifest(raw_path: Path, root: Path = ARTIFACTS) -> dict[str, object]:
    """Hash every published artifact (and the raw input) into ``metadata/manifest.json``."""
    manifest: dict[str, object] = {
        "dados_brutos": {
            "arquivo": raw_path.name,
            "bytes": raw_path.stat().st_size,
            "sha256": sha256_of(raw_path),
            **RAW_SOURCE,
        },
        "artefatos": {
            path.relative_to(root).as_posix(): sha256_of(path) for path in _published(root)
        },
        "reproducao": REPRODUCTION_STEPS,
    }
    (root / MANIFEST).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def verify_manifest(root: Path = ARTIFACTS, raw_path: Path | None = None) -> dict[str, str]:
    """Compare published files with ``metadata/manifest.json``.

    Returns ``{relative path: status}`` with status ``ok``, ``alterado`` (hash differs),
    ``ausente`` (listed but missing) or ``nao_registrado`` (published but not listed).
    The raw file is checked under the key ``data/raw/<name>`` when it exists locally.
    """
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    expected: dict[str, str] = dict(manifest["artefatos"])
    raw = manifest.get("dados_brutos", {})
    raw_file = raw_path or root / "data" / "raw" / raw.get("arquivo", "")
    if raw and raw_file.is_file():
        expected[f"data/raw/{raw_file.name}"] = raw["sha256"]
        found = {f"data/raw/{raw_file.name}": raw_file}
    else:
        found = {}
    found |= {path.relative_to(root).as_posix(): path for path in _published(root)}
    status: dict[str, str] = {}
    for relative, digest in expected.items():
        path = found.get(relative)
        if path is None:
            status[relative] = "ausente"
        else:
            status[relative] = "ok" if sha256_of(path) == digest else "alterado"
    for relative in found.keys() - expected.keys():
        status[relative] = "nao_registrado"
    return dict(sorted(status.items()))


class ArtifactStore:
    def __init__(self, root: Path = ARTIFACTS) -> None:
        self.root = root

    def _required(self, relative: str) -> Path:
        path = self.root / relative
        if not path.exists():
            raise FileNotFoundError(
                f"Artefato ausente: {path}. Publique-o pelos notebooks ou pipeline."
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
