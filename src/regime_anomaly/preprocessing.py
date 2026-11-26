"""Preprocessing for the Steel Industry Energy Consumption dataset.

Two APIs live here:

* **Protocol pipeline** (notebooks 02b-05 and the published ``ModelBundle``):
  :func:`prepare_frame` repairs timestamps, validates, adds calendar features and assigns
  the chronological train/validation/test split; :func:`build_feature_preprocessor`
  returns an unfitted transformer for a named feature set. These functions accept the
  original UCI column names returned by :func:`regime_anomaly.data.load_data` and work
  internally on snake_case names (see :func:`normalize_columns`).
* **Configuration exploration** (notebook 02): :func:`build_preprocessor`,
  :func:`describe_preprocessor` and the ``FEATURE_*`` lists, on original UCI names.

Anything that learns statistics from the data is returned unfitted and must be fitted
on the training period only.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from .config import RANDOM_STATE
from .data import LABEL_COLUMN, snake_case

DATE_COLUMN = "date"
TIMESTAMP_COLUMN = "timestamp"
SPLIT_COLUMN = "split"
LABEL = snake_case(LABEL_COLUMN)  # "load_type" after normalize_columns

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


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with snake_case column names (``Usage_kWh`` -> ``usage_kwh``).

    Idempotent, so frames that are already snake_case pass through unchanged.
    """
    result = frame.rename(columns=snake_case)
    if len(result.columns) and result.columns[0] == "unnamed_0":
        result = result.rename(columns={"unnamed_0": "record_id"})
    return result


def parse_timestamps(frame: pd.DataFrame) -> pd.DataFrame:
    """Add a corrected ``timestamp`` column and return rows in chronological order.

    The source labels each reading by the end of its 15-minute interval. The reading
    that closes a day (24:00) is stored after 23:45 with that same calendar date and
    ``NSM == 0``, so a naive parse places it 24 hours too early. Those rows are moved
    to the following midnight. ``day_of_week`` and ``weekstatus`` keep the source
    convention (the day the interval belongs to).
    """
    result = normalize_columns(frame)
    result[TIMESTAMP_COLUMN] = chronological_timestamps(result)
    return result.sort_values(TIMESTAMP_COLUMN, kind="stable").reset_index(drop=True)


def chronological_timestamps(frame: pd.DataFrame) -> pd.Series:
    """Corrected end-of-interval timestamps for the source ``date`` column."""
    frame = normalize_columns(frame)
    values = frame[DATE_COLUMN].astype(str)
    # UCI layout first (dd/mm/yyyy HH:MM); anything else must be ISO 8601. A bare
    # dayfirst parse misreads ISO strings as %Y-%d-%m and fails on days above 12.
    parsed = pd.to_datetime(values, format="%d/%m/%Y %H:%M", errors="coerce")
    other = parsed.isna()
    if other.any():
        parsed[other] = pd.to_datetime(values[other], format="ISO8601", errors="raise")
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
    """Guard against Load_Type entering any model input (original or snake_case name)."""
    if {LABEL_COLUMN, LABEL} & set(columns):
        raise ValueError(f"{LABEL_COLUMN} não pode ser usado como feature.")


def feature_columns(feature_set: str) -> list[str]:
    """Model input columns for a named feature set."""
    try:
        columns = FEATURE_SETS[feature_set].columns
    except KeyError as error:
        raise KeyError(f"Conjunto de features desconhecido: {feature_set}") from error
    assert_no_label(columns)
    return columns


def build_feature_preprocessor(feature_set: str) -> ColumnTransformer:
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


# ---------------------------------------------------------------------------------------
# Configuration exploration (notebook 02). Original UCI column names.
# ---------------------------------------------------------------------------------------
TIME_COLUMN = "date"

FEATURE_NUMERIC = [
    "Usage_kWh",  # feature central
    "Lagging_Current_Reactive.Power_kVarh",  # r=0.9 com o 'Usage_kWh'
    "Leading_Current_Reactive_Power_kVarh",  # r=-0.32 com o 'Usage_kWh'
    "Lagging_Current_Power_Factor",  # r=0.39 com o 'Usage_kWh'
]
FEATURE_HOUR = ["hour_sin", "hour_cos"]
FEATURE_MONTH = ["month_sin", "month_cos"]
FEATURE_CATEGORICAL = ["Day_of_week"]

# Used only to validate/report clusters; excluded from K-Means.
FEATURE_REPORTED = [
    "CO2(tCO2)",  # r=0.99 com o 'Usage_kWh' -> excluída no K-Means e mantida para validar e reportar os clusters
    "WeekStatus",  # redundante com o Day_of_week
]

# Replaced by cyclic hour and month features.
FEATURE_DELETED = ["date", "NSM"]


FEATURE_CONFIGS = {
    "Base (Todas as Features Numéricas)": (FEATURE_NUMERIC, None),
    "Base + hora": (FEATURE_NUMERIC + FEATURE_HOUR, None),
    "Base + mês": (FEATURE_NUMERIC + FEATURE_MONTH, None),
    "Base + hora + mês": (FEATURE_NUMERIC + FEATURE_HOUR + FEATURE_MONTH, None),
    "Base + Day_of_week": (FEATURE_NUMERIC + ["Day_of_week"], None),
    "Base + Day_of_week + PCA90": (FEATURE_NUMERIC + ["Day_of_week"], 0.9),
}


def time_feature_adapt(data: pd.DataFrame) -> pd.DataFrame:
    """Replace raw temporal columns with cyclic hour and month features."""
    output = data.copy()
    output["hour_sin"] = np.sin(2 * np.pi * output[TIME_COLUMN].dt.hour / 24)
    output["hour_cos"] = np.cos(2 * np.pi * output[TIME_COLUMN].dt.hour / 24)
    output["month_sin"] = np.sin(2 * np.pi * (output[TIME_COLUMN].dt.month - 1) / 12)
    output["month_cos"] = np.cos(2 * np.pi * (output[TIME_COLUMN].dt.month - 1) / 12)
    return output.drop(columns=FEATURE_DELETED, errors="ignore")


def split_columns(columns: list[str]) -> tuple[list[str], list[str]]:
    """Split a column list into numeric and categorical columns."""
    categorical = [column for column in columns if column in FEATURE_CATEGORICAL]
    numeric = [column for column in columns if column not in FEATURE_CATEGORICAL]
    return numeric, categorical


def build_preprocessor(
    numeric_cols: list[str] | None = None,
    categorical_cols: list[str] | None = None,
    pca_variance: float | None = 0.90,
) -> Pipeline:
    """Build the preprocessing pipeline used by the analysis notebooks."""

    numeric_cols = numeric_cols or []
    categorical_cols = categorical_cols or []

    column_preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_cols,
            ),
        ]
    )

    steps: list[tuple[str, Any]] = [
        ("time", FunctionTransformer(time_feature_adapt, validate=False)),
        ("prep", column_preprocessor),
    ]

    if pca_variance is not None:
        steps.append(("pca", PCA(n_components=pca_variance, random_state=RANDOM_STATE)))

    return Pipeline(steps=steps)


def describe_preprocessor(pipeline: Pipeline) -> dict[str, object]:
    """Return serializable metadata for a fitted preprocessing pipeline."""
    columns: ColumnTransformer = pipeline.named_steps["prep"]
    fitted = {
        name: list(selected_columns)
        for name, _, selected_columns in columns.transformers_
        if name != "remainder"
    }
    numeric = fitted.get("num", [])
    categorical = fitted.get("cat", [])
    derived = set(FEATURE_HOUR + FEATURE_MONTH)
    required = [TIME_COLUMN] + [column for column in numeric + categorical if column not in derived]

    pca: PCA | None = pipeline.named_steps.get("pca")
    ratio = [float(value) for value in pca.explained_variance_ratio_] if pca is not None else []
    categorical_transformer = columns.named_transformers_["cat"]
    return {
        "feature_numeric": numeric,
        "feature_categorical": categorical,
        "feature_reporting_only": FEATURE_REPORTED,
        "feature_deleted": FEATURE_DELETED,
        "one_hot_features": (
            list(categorical_transformer.get_feature_names_out(categorical)) if categorical else []
        ),
        "required_columns": required,
        "pca_components": [f"PC{index + 1}" for index in range(len(ratio))],
        "explained_variance_ratio": ratio,
        "cumulative_variance": [float(value) for value in np.cumsum(ratio)],
    }


def evaluate_config(cols: list[str], X, y, pca: float | None) -> tuple[float, float]:
    """
    Além de Pre-Processar os dados, treina o K-Means e
    avalia os resultados por meio das métricas Silhouette e ARI
    """
    numeric, categorical = split_columns(cols)
    pipeline = build_preprocessor(
        numeric_cols=numeric, categorical_cols=categorical, pca_variance=pca
    )

    X_prep = pipeline.fit_transform(X)

    km = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X_prep)
    silhouette_scalled = silhouette_score(X_prep, km.labels_)
    ari_score = adjusted_rand_score(y, km.labels_)

    return silhouette_scalled, ari_score


def create_silhouette_ari_dataframe(configs: dict, X_train, y_train) -> pd.DataFrame:
    results = []
    for name, (cols, pca) in configs.items():
        sil, ari = evaluate_config(cols, X_train, y_train, pca=pca)
        results.append({"Config": name, "Silhouette": sil, "ARI": ari})

    return pd.DataFrame(results)
