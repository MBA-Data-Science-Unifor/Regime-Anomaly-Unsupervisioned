"""Model construction and the serialized bundle consumed by the application.

Experiments and selection live in ``artifacts/notebooks/03_Modeling.ipynb``; this module
keeps only what must be identical between the notebook and inference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.mixture import GaussianMixture

from . import preprocessing as pp
from .config import RANDOM_STATE

N_REGIMES = 3
REGIME_CANDIDATES: dict[str, dict[str, Any]] = {
    "kmeans": {"algorithm": "kmeans"},
    "gmm_diag": {"algorithm": "gmm", "covariance_type": "diag"},
    "gmm_full": {"algorithm": "gmm", "covariance_type": "full"},
}
INPUT_COLUMNS = [
    *pp.ENERGY_COLUMNS,
    *pp.POWER_FACTOR_COLUMNS,
    pp.NSM,
    pp.WEEK_STATUS,
    pp.DAY_OF_WEEK,
]


def make_regime_model(candidate: str, seed: int = RANDOM_STATE) -> KMeans | GaussianMixture:
    """Unfitted three-regime model for a named candidate."""
    spec = REGIME_CANDIDATES[candidate]
    if spec["algorithm"] == "kmeans":
        return KMeans(n_clusters=N_REGIMES, n_init=20, random_state=seed)
    return GaussianMixture(
        n_components=N_REGIMES,
        covariance_type=spec["covariance_type"],
        n_init=5,
        max_iter=500,
        random_state=seed,
    )


def make_anomaly_model(seed: int = RANDOM_STATE) -> IsolationForest:
    """Isolation Forest whose threshold is set externally, not by ``contamination``."""
    return IsolationForest(n_estimators=300, max_samples="auto", n_jobs=-1, random_state=seed)


REGIME_NAMES = ["ocioso indutivo", "ocioso capacitivo", "produção"]


def order_by_profile(labels: np.ndarray, frame: pd.DataFrame) -> dict[int, int]:
    """Map raw cluster ids to the fixed order of ``REGIME_NAMES`` by electrical profile.

    Production is the cluster with the highest median usage; among the remaining two,
    the capacitive one has the highest median leading reactive energy. Naming by profile
    rather than by usage rank keeps the two idle regimes (with near-equal usage) from
    swapping names between fits.
    """
    if len(np.unique(labels)) != N_REGIMES:
        raise ValueError(f"São esperados {N_REGIMES} grupos.")
    medians = frame[[pp.USAGE, pp.LEADING_KVARH]].groupby(np.asarray(labels)).median()
    production = int(medians[pp.USAGE].to_numpy().argmax())
    idle = medians.drop(index=medians.index[production])
    capacitive = int(idle[pp.LEADING_KVARH].to_numpy().argmax())
    inductive = 1 - capacitive
    return {
        int(idle.index[inductive]): 0,
        int(idle.index[capacitive]): 1,
        int(medians.index[production]): 2,
    }


def regime_boundaries(regimes: np.ndarray, timestamps: pd.Series | None = None) -> np.ndarray:
    """Flag readings whose regime differs from the previous or next reading.

    Neighbours are taken in chronological order when ``timestamps`` is given (and only
    across consecutive 15-minute readings, so gaps never create boundaries); otherwise
    in row order. The result is aligned with the input rows.
    """
    regimes = np.asarray(regimes)
    if len(regimes) == 0:
        return np.zeros(0, dtype=bool)
    if timestamps is None:
        positions = np.arange(len(regimes))
        consecutive = np.ones(len(regimes) - 1, dtype=bool)
    else:
        times = pd.to_datetime(pd.Series(timestamps)).to_numpy()
        positions = np.argsort(times, kind="stable")
        steps = np.diff(times[positions])
        consecutive = steps == np.timedelta64(pp.EXPECTED_FREQUENCY)

    ordered = regimes[positions]
    changes = (ordered[1:] != ordered[:-1]) & consecutive
    boundary_sorted = np.zeros(len(ordered), dtype=bool)
    boundary_sorted[1:] |= changes
    boundary_sorted[:-1] |= changes

    boundary = np.empty_like(boundary_sorted)
    boundary[positions] = boundary_sorted
    return boundary


def _timestamps_of(frame: pd.DataFrame) -> pd.Series | None:
    if pp.TIMESTAMP_COLUMN in frame.columns:
        return pd.to_datetime(frame[pp.TIMESTAMP_COLUMN])
    if pp.DATE_COLUMN in frame.columns:
        return pp.chronological_timestamps(frame)
    return None


@dataclass
class ModelBundle:
    """Fitted preprocessing, regime and anomaly models plus their metadata."""

    regime_feature_set: str
    regime_preprocessor: Any
    regime_model: Any
    regime_order: dict[int, int]
    regime_names: list[str]
    anomaly_feature_set: str
    anomaly_preprocessor: Any
    anomaly_model: Any
    anomaly_threshold: float
    # Suppress alerts on regime boundaries (15-minute readings that straddle a state
    # change). Bundles pickled before this field existed fall back to False.
    transition_filter: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def _features(self, frame: pd.DataFrame) -> pd.DataFrame:
        missing = [column for column in INPUT_COLUMNS if column not in frame.columns]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
        unknown = sorted(set(frame[pp.DAY_OF_WEEK]) - set(pp.DAY_ORDER))
        if unknown:
            raise ValueError(f"Dias da semana desconhecidos: {unknown}")
        pp.assert_no_label(pp.feature_columns(self.regime_feature_set))
        return pp.add_calendar_features(frame)

    def anomaly_scores(self, frame: pd.DataFrame) -> np.ndarray:
        """Higher means more unusual; comparable with ``anomaly_threshold``."""
        features = self._features(frame)
        columns = pp.feature_columns(self.anomaly_feature_set)
        transformed = self.anomaly_preprocessor.transform(features[columns])
        return -self.anomaly_model.score_samples(transformed)

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Assign a regime and an anomaly flag to each row of a snake_case frame."""
        features = self._features(frame)
        regime_input = self.regime_preprocessor.transform(
            features[pp.feature_columns(self.regime_feature_set)]
        )
        raw_labels = self.regime_model.predict(regime_input)
        regime = np.vectorize(self.regime_order.__getitem__)(raw_labels)

        result = frame.copy()
        result["regime"] = regime
        result["regime_name"] = [self.regime_names[value] for value in regime]
        if hasattr(self.regime_model, "predict_proba"):
            result["regime_confidence"] = self.regime_model.predict_proba(regime_input).max(axis=1)
        result["anomaly_score"] = self.anomaly_scores(frame)
        result["is_anomaly_raw"] = result["anomaly_score"] >= self.anomaly_threshold
        result["regime_boundary"] = regime_boundaries(regime, _timestamps_of(frame))
        result["is_anomaly"] = result["is_anomaly_raw"]
        if self.transition_filter:
            result["is_anomaly"] = result["is_anomaly_raw"] & ~result["regime_boundary"]
        return result
