""" Streamlit Pre-Processing adaptation """

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from regime_anomaly.config import RANDOM_STATE


TIME_COLUMN = "date"

FEATURE_NUMERIC = [
    "usage_kwh",  # feature central
    "lagging_current_reactive_power_kvarh",  # r=0.9 com usage_kwh
    "leading_current_reactive_power_kvarh",  # r=-0.32 com usage_kwh
    "lagging_current_power_factor",  # r=0.39 com usage_kwh
]
FEATURE_HOUR = ["hour_sin", "hour_cos"]
FEATURE_MONTH = ["month_sin", "month_cos"]
FEATURE_CATEGORICAL = ["day_of_week"]

# Mantidas só para validar/reportar clusters; fora do K-Means
FEATURE_REPORTED = ["co2_tco2", "weekstatus"]

# Substituídas pelas features cíclicas de hora e mês
FEATURE_DELETED = ["date", "nsm"]



def time_feature_adapt(data: pd.DataFrame) -> pd.DataFrame:
    """
    Será realizado a adaptação das colunas relacionadas a tempo, 
    de modo a alinhar melhor a distância entre os pontos
    (não será adpatado a data para dia da semana por 
    apresentar redundância com a coluna 'Day_of_Week')
    """
    out = data.copy()
    
    out['hour_sin'] = np.sin(2 * np.pi * out["date"].dt.hour / 24)
    out['hour_cos'] = np.cos(2 * np.pi * out["date"].dt.hour / 24)
    out["month_sin"] = np.sin(2 * np.pi * (out["date"].dt.month - 1) / 12)
    out["month_cos"] = np.cos(2 * np.pi * (out["date"].dt.month - 1) / 12)

    return out.drop(columns=FEATURE_DELETED, erros="ignore")


def split_columns(cols: list[str]) -> tuple[list[str], list[str]]:
    """ Separa uma lista de colunas em (numéricas, categóricas). """
    categorical = [c for c in cols if c in FEATURE_CATEGORICAL]
    numeric = [c for c in cols if c not in FEATURE_CATEGORICAL]
    return numeric, categorical



def build_preprocessor(
        numeric_cols: list[str] | None = None,
        categorical_cols: list[str] | None = None,
        pca_variance: float | None = 0.90
) -> Pipeline:
    """
    Construção do Pré-Processamento de dados, recebendo um dataFrame cru,
    adaptando a escala das colunas numéricas e adaptando as colunas categóricas
    """
    column_preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols)
        ]
    )

    steps = [
        ("time", FunctionTransformer(time_feature_adapt, validate=False)),
        ("prep", ColumnTransformer(column_preprocessor)),
    ]

    if pca_variance is not None:
        steps.append(("pca", PCA(n_components=pca_variance, random_state=RANDOM_STATE)))

    return Pipeline(steps=steps)


def describe_preprocessor(pipeline: Pipeline):
    """Resumo JSON do pipeline fornecido"""
    columns = pipeline.named_steps["prep"]
    pca = pipeline.named_steps["pca"]
    
    fitted = {name: list(cols) for name, _, cols in columns.transformers_ if name != "remainder"}
    
    numeric = fitted.get("num", [])
    categorical = fitted.get("cat", [])

    derived = set(FEATURE_HOUR + FEATURE_MONTH)
    required = [TIME_COLUMN] + [c for c in numeric + categorical if c not in derived]

    ratio = [float(v) for v in pca.explained_variance_ratio_]
    return {
        "feature_numeric": numeric,
        "feature_categorical": categorical,
        "feature_reporting_only": FEATURE_REPORTED,
        "feature_deleted": FEATURE_DELETED,
        "one_hot_features": (
            list(columns.named_transformers_["cat"].get_feature_names_out(categorical))
            if categorical else []
        ),
        
        "required_columns": required,
        "pca_components": [f"PC{i + 1}" for i in range(len(ratio))],
        "explained_variance_ratio": ratio,
        "cumulative_variance": [float(v) for v in np.cumsum(ratio)],
    }
