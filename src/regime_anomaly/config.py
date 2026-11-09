"""Central project paths and modelling constants."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
RAW_DIR = ARTIFACTS / "data" / "raw"
PROCESSED_DIR = ARTIFACTS / "data" / "processed"
TABLES_DIR = ARTIFACTS / "tables"
IMAGES_DIR = ARTIFACTS / "images"
MODELS_DIR = ARTIFACTS / "models"
METADATA_DIR = ARTIFACTS / "metadata"

RANDOM_STATE = 42


def ensure_artifact_dirs() -> None:
    """Create the complete output contract used by the pipeline and app."""
    for directory in (
        RAW_DIR,
        PROCESSED_DIR,
        TABLES_DIR,
        IMAGES_DIR,
        MODELS_DIR,
        METADATA_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
