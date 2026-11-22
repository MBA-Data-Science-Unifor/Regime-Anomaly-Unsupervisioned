"""Public API for the energy-consumption regime and anomaly project.

Import reusable objects from this module in notebooks and applications so those
clients do not need to know the package's internal module layout.
"""

from .artifacts import ArtifactStore
from .config import (
    ARTIFACTS,
    IMAGES_DIR,
    METADATA_DIR,
    MODELS_DIR,
    PROCESSED_DIR,
    RANDOM_STATE,
    RAW_DIR,
    ROOT,
    TABLES_DIR,
    ensure_artifact_dirs,
)
from .data import DEFAULT_DATASET, LABEL_COLUMN, load_data
from .i18n import (
    DEFAULT_LOCALE,
    LOCALE_LABELS,
    SUPPORTED_LOCALES,
    translate,
    translations,
)
from .modeling import ModelBundle
from .pipeline import ARTIFACT_CONTRACT
from .preprocessing import (
    FEATURE_CATEGORICAL,
    FEATURE_DELETED,
    FEATURE_HOUR,
    FEATURE_MONTH,
    FEATURE_NUMERIC,
    FEATURE_REPORTED,
    TIME_COLUMN,
    build_preprocessor,
    describe_preprocessor,
    split_columns,
    time_feature_adapt,
)

__version__ = "0.1.0"

__all__ = [
    "ARTIFACTS",
    "ARTIFACT_CONTRACT",
    "DEFAULT_DATASET",
    "DEFAULT_LOCALE",
    "FEATURE_CATEGORICAL",
    "FEATURE_DELETED",
    "FEATURE_HOUR",
    "FEATURE_MONTH",
    "FEATURE_NUMERIC",
    "FEATURE_REPORTED",
    "IMAGES_DIR",
    "LABEL_COLUMN",
    "LOCALE_LABELS",
    "METADATA_DIR",
    "MODELS_DIR",
    "PROCESSED_DIR",
    "RANDOM_STATE",
    "RAW_DIR",
    "ROOT",
    "SUPPORTED_LOCALES",
    "TABLES_DIR",
    "TIME_COLUMN",
    "ArtifactStore",
    "ModelBundle",
    "__version__",
    "build_preprocessor",
    "describe_preprocessor",
    "ensure_artifact_dirs",
    "load_data",
    "split_columns",
    "time_feature_adapt",
    "translate",
    "translations",
]
