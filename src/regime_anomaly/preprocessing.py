"""Reusable preprocessing utilities for notebooks and the application."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score

from .config import RANDOM_STATE

TIME_COLUMN = "date"

FEATURE_NUMERIC = [
    'Usage_kWh', # feature central
    'Lagging_Current_Reactive.Power_kVarh',  # r=0.9 com o 'Usage_kWh'
    'Leading_Current_Reactive_Power_kVarh',  # r=-0.32 com o 'Usage_kWh'
    'Lagging_Current_Power_Factor'           # r=0.39 com o 'Usage_kWh'
]
FEATURE_HOUR = ["hour_sin", "hour_cos"]
FEATURE_MONTH = ["month_sin", "month_cos"]
FEATURE_CATEGORICAL = ["Day_of_week"]

# Used only to validate/report clusters; excluded from K-Means.
FEATURE_REPORTED = [
    "CO2(tCO2)", # r=0.99 com o 'Usage_kWh' -> excluída no K-Means e mantida para validar e reportar os clusters
    "WeekStatus" # redundante com o Day_of_week
]

# Replaced by cyclic hour and month features.
FEATURE_DELETED = ["date", "NSM"]


FEATURE_CONFIGS = {
    "Base (Todas as Features Numéricas)": (FEATURE_NUMERIC, None),
    "Base + hora": (FEATURE_NUMERIC + FEATURE_HOUR, None),
    "Base + mês": (FEATURE_NUMERIC + FEATURE_MONTH, None),
    "Base + hora + mês": (FEATURE_NUMERIC + FEATURE_HOUR + FEATURE_MONTH, None),
    "Base + Day_of_week": (FEATURE_NUMERIC + ['Day_of_week'], None),
    "Base + Day_of_week + PCA90": (FEATURE_NUMERIC + ['Day_of_week'], 0.9)
}




def time_feature_adapt(data: pd.DataFrame) -> pd.DataFrame:
    """Replace raw temporal columns with cyclic hour and month features."""
    output = data.copy()
    output["hour_sin"] = np.sin(2 * np.pi * output[TIME_COLUMN].dt.hour / 24)
    output["hour_cos"] = np.cos(2 * np.pi * output[TIME_COLUMN].dt.hour / 24)
    output["month_sin"] = np.sin(
        2 * np.pi * (output[TIME_COLUMN].dt.month - 1) / 12
    )
    output["month_cos"] = np.cos(
        2 * np.pi * (output[TIME_COLUMN].dt.month - 1) / 12
    )
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
    required = [TIME_COLUMN] + [
        column for column in numeric + categorical if column not in derived
    ]

    pca: PCA | None = pipeline.named_steps.get("pca")
    ratio = (
        [float(value) for value in pca.explained_variance_ratio_]
        if pca is not None
        else []
    )
    categorical_transformer = columns.named_transformers_["cat"]
    return {
        "feature_numeric": numeric,
        "feature_categorical": categorical,
        "feature_reporting_only": FEATURE_REPORTED,
        "feature_deleted": FEATURE_DELETED,
        "one_hot_features": (
            list(categorical_transformer.get_feature_names_out(categorical))
            if categorical
            else []
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
    pipeline = build_preprocessor(numeric_cols=numeric, categorical_cols=categorical, pca_variance=pca)

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
