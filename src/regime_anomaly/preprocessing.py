"""Leakage-safe preparation for the Steel Industry Energy Consumption dataset.

Every function here operates on the snake_case frame returned by
:func:`regime_anomaly.data.load_data`. Row-local steps (timestamp repair and calendar
features) can run on the full dataset; anything that learns statistics from the data is
returned as an unfitted scikit-learn transformer that must be fitted on the training
period only.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from .data import LABEL_COLUMN

DATE_COLUMN = "date"
TIMESTAMP_COLUMN = "timestamp"
SPLIT_COLUMN = "split"

USAGE = "usage_kwh"
LAGGING_KVARH = "lagging_current_reactive_power_kvarh"
LEADING_KVARH = "leading_current_reactive_power_kvarh"
CO2 = "co2_tco2"
LAGGING_PF = "lagging_current_power_factor"
LEADING_PF = "leading_current_power_factor"
NSM = "nsm"
WEEK_STATUS = "weekstatus"
DAY_OF_WEEK = "day_of_week"

ELECTRICAL_COLUMNS = [USAGE, LAGGING_KVARH, LEADING_KVARH, CO2, LAGGING_PF, LEADING_PF]
ENERGY_COLUMNS = [USAGE, LAGGING_KVARH, LEADING_KVARH]
POWER_FACTOR_COLUMNS = [LAGGING_PF, LEADING_PF]
CALENDAR_FEATURES = ["hour_sin", "hour_cos", "dow_sin", "dow_cos", "is_weekend"]

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEK_STATUS_VALUES = {"Weekday", "Weekend"}
EXPECTED_FREQUENCY = pd.Timedelta(minutes=15)
SECONDS_PER_DAY = 86_400

# Chronological boundaries (exclusive upper bounds): Jan-Aug train, Sep-Oct validation,
# Nov-Dec test. The test period is frozen until the final evaluation.
DEFAULT_SPLIT_BOUNDARIES = (pd.Timestamp("2018-09-01"), pd.Timestamp("2018-11-01"))
SPLIT_NAMES = ("train", "validation", "test")


def log1p_energy(values: np.ndarray) -> np.ndarray:
    """Compress the right tail of non-negative energy readings."""
    return np.log1p(values)


def log1p_power_factor_deficit(values: np.ndarray) -> np.ndarray:
    """Map a 0-100 power factor to log(1 + distance from unity).

    Leading power factor piles up at 100 with a long left tail; the deficit turns that
    into a right tail that ``log1p`` can compress, and stays interpretable.
    """
    return np.log1p(100.0 - values)


@dataclass(frozen=True)
class FeatureSet:
    """Columns entering a model, grouped by the transformation they receive."""

    energy: tuple[str, ...]
    power_factor: tuple[str, ...]
    passthrough_scaled: tuple[str, ...] = ()

    @property
    def columns(self) -> list[str]:
        return [*self.energy, *self.power_factor, *self.passthrough_scaled]


# "regime" deliberately excludes calendar features: Load_Type follows a time-of-use
# schedule, so calendar inputs would let clusters reproduce the tariff table instead
# of electrical behaviour. CO2 is excluded everywhere because it is a quantized,
# near-linear copy of usage (Pearson ~0.99).
FEATURE_SETS: dict[str, FeatureSet] = {
    "regime": FeatureSet(
        energy=tuple(ENERGY_COLUMNS),
        power_factor=tuple(POWER_FACTOR_COLUMNS),
    ),
    "regime_with_calendar": FeatureSet(
        energy=tuple(ENERGY_COLUMNS),
        power_factor=tuple(POWER_FACTOR_COLUMNS),
        passthrough_scaled=tuple(CALENDAR_FEATURES),
    ),
    "anomaly": FeatureSet(
        energy=tuple(ENERGY_COLUMNS),
        power_factor=tuple(POWER_FACTOR_COLUMNS),
        passthrough_scaled=("hour_sin", "hour_cos", "is_weekend"),
    ),
}


def parse_timestamps(frame: pd.DataFrame) -> pd.DataFrame:
    """Add a corrected ``timestamp`` column and return rows in chronological order.

    The source labels each reading by the end of its 15-minute interval. The reading
    that closes a day (24:00) is stored after 23:45 with that same calendar date and
    ``NSM == 0``, so a naive parse places it 24 hours too early. Those rows are moved
    to the following midnight. ``day_of_week`` and ``weekstatus`` keep the source
    convention (the day the interval belongs to).
    """
    result = frame.copy()
    result[TIMESTAMP_COLUMN] = chronological_timestamps(result)
    return result.sort_values(TIMESTAMP_COLUMN, kind="stable").reset_index(drop=True)


def chronological_timestamps(frame: pd.DataFrame) -> pd.Series:
    """Corrected end-of-interval timestamps for the source ``date`` column."""
    parsed = pd.to_datetime(frame[DATE_COLUMN], dayfirst=True, errors="raise")
    closes_day = (parsed.dt.hour == 0) & (parsed.dt.minute == 0)
    return parsed + pd.to_timedelta(closes_day.astype(int), unit="D")


def validate_frame(frame: pd.DataFrame) -> dict[str, object]:
    """Fail on structural problems and return a small quality report."""
    required = {TIMESTAMP_COLUMN, *ELECTRICAL_COLUMNS, NSM, WEEK_STATUS, DAY_OF_WEEK}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Colunas ausentes: {missing}")

    nulls = int(frame[sorted(required)].isna().sum().sum())
    duplicated = int(frame[TIMESTAMP_COLUMN].duplicated().sum())
    steps = frame[TIMESTAMP_COLUMN].diff().dropna()
    irregular = int((steps != EXPECTED_FREQUENCY).sum())
    unknown_days = sorted(set(frame[DAY_OF_WEEK]) - set(DAY_ORDER))
    unknown_status = sorted(set(frame[WEEK_STATUS]) - WEEK_STATUS_VALUES)
    negative = int((frame[ENERGY_COLUMNS] < 0).sum().sum())
    pf_out_of_range = int(
        ((frame[POWER_FACTOR_COLUMNS] < 0) | (frame[POWER_FACTOR_COLUMNS] > 100)).sum().sum()
    )

    problems = {
        "valores_nulos": nulls,
        "timestamps_duplicados": duplicated,
        "intervalos_irregulares": irregular,
        "energia_negativa": negative,
        "fator_potencia_fora_0_100": pf_out_of_range,
        "dias_desconhecidos": len(unknown_days),
        "status_desconhecidos": len(unknown_status),
    }
    failed = {name: count for name, count in problems.items() if count}
    if failed:
        raise ValueError(f"Falha de validação: {failed}")

    return {
        "linhas": len(frame),
        "inicio": frame[TIMESTAMP_COLUMN].min().isoformat(),
        "fim": frame[TIMESTAMP_COLUMN].max().isoformat(),
        **problems,
    }


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add cyclical hour/day encodings and a weekend flag (row-local, no fitting)."""
    result = frame.copy()
    day_angle = 2 * np.pi * result[NSM] / SECONDS_PER_DAY
    day_index = result[DAY_OF_WEEK].map({day: i for i, day in enumerate(DAY_ORDER)})
    week_angle = 2 * np.pi * day_index / len(DAY_ORDER)
    result["hour_sin"] = np.sin(day_angle)
    result["hour_cos"] = np.cos(day_angle)
    result["dow_sin"] = np.sin(week_angle)
    result["dow_cos"] = np.cos(week_angle)
    result["is_weekend"] = (result[WEEK_STATUS] == "Weekend").astype(float)
    return result


def assign_split(
    frame: pd.DataFrame,
    boundaries: Sequence[pd.Timestamp] = DEFAULT_SPLIT_BOUNDARIES,
) -> pd.DataFrame:
    """Label each row train/validation/test by chronological boundaries.

    Timestamps mark the end of a reading's interval, so a reading stamped exactly at a
    boundary closes the earlier period and stays on that side.
    """
    if len(boundaries) != len(SPLIT_NAMES) - 1:
        raise ValueError("São necessárias duas fronteiras para três partições.")
    if list(boundaries) != sorted(boundaries):
        raise ValueError("As fronteiras precisam estar em ordem crescente.")
    result = frame.copy()
    position = np.searchsorted(
        np.asarray(boundaries, dtype="datetime64[ns]"),
        result[TIMESTAMP_COLUMN].to_numpy(dtype="datetime64[ns]"),
        side="left",
    )
    result[SPLIT_COLUMN] = np.asarray(SPLIT_NAMES)[position]
    return result


def prepare_frame(
    frame: pd.DataFrame,
    boundaries: Sequence[pd.Timestamp] = DEFAULT_SPLIT_BOUNDARIES,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Run every row-local step: timestamp repair, validation, calendar, split."""
    prepared = parse_timestamps(frame)
    report = validate_frame(prepared)
    prepared = assign_split(add_calendar_features(prepared), boundaries)
    return prepared, report


def assert_no_label(columns: Iterable[str]) -> None:
    """Guard against Load_Type entering any model input."""
    if LABEL_COLUMN in set(columns):
        raise ValueError(f"{LABEL_COLUMN} não pode ser usado como feature.")


def feature_columns(feature_set: str) -> list[str]:
    """Model input columns for a named feature set."""
    try:
        columns = FEATURE_SETS[feature_set].columns
    except KeyError as error:
        raise KeyError(f"Conjunto de features desconhecido: {feature_set}") from error
    assert_no_label(columns)
    return columns


def build_preprocessor(feature_set: str) -> ColumnTransformer:
    """Return an unfitted transformer for the named feature set.

    Fit it on the training split only; it then transforms validation and test with
    training statistics.
    """
    spec = FEATURE_SETS[feature_set]
    assert_no_label(spec.columns)

    def scaled(function: object) -> Pipeline:
        transformer = FunctionTransformer(function, feature_names_out="one-to-one")
        return make_pipeline(transformer, StandardScaler())

    transformers: list[tuple[str, object, list[str]]] = [
        ("energy", scaled(log1p_energy), list(spec.energy)),
        ("power_factor", scaled(log1p_power_factor_deficit), list(spec.power_factor)),
    ]
    if spec.passthrough_scaled:
        transformers.append(("calendar", StandardScaler(), list(spec.passthrough_scaled)))

    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)
