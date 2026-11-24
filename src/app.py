"""Streamlit app that reads published artifacts and never trains or rewrites them."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from regime_anomaly.artifacts import ArtifactStore
from regime_anomaly.config import ARTIFACTS
from regime_anomaly.data import snake_case
from regime_anomaly.i18n import (
    DEFAULT_LOCALE,
    LOCALE_LABELS,
    SUPPORTED_LOCALES,
    translate,
)

st.set_page_config(page_title="Steel Energy Regimes", page_icon="⚡", layout="wide")
store = ArtifactStore()
RESULTS = "data/processed/analysis_results.csv"


def artifact_exists(relative: str) -> bool:
    return (ARTIFACTS / relative).exists()


@st.cache_data
def load_results() -> pd.DataFrame:
    frame = store.results()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    return frame


def overview(locale: str) -> None:
    st.title(translate("overview.title", locale))
    st.caption(translate("overview.caption", locale))
    if not artifact_exists("metadata/final_metrics.json"):
        st.info(translate("overview.no_metrics", locale))
        return
    metrics: dict[str, Any] = store.metrics()
    model, test = metrics["modelo"], metrics["teste"]
    columns = st.columns(4)
    columns[0].metric(
        translate("overview.model", locale), f"{model['candidato']} · {model['conjunto']}"
    )
    columns[1].metric(translate("overview.test_silhouette", locale), f"{test['silhouette']:.3f}")
    columns[2].metric(
        translate("overview.stability", locale),
        f"{metrics['validacao']['ari_bootstrap_media']:.3f}",
    )
    transition_filter = metrics.get("filtro_transicao")
    if transition_filter:
        filtered_rate = transition_filter["por_particao"]["test"]["taxa_com_filtro"]
        columns[3].metric(
            translate("overview.alert_rate_filtered", locale),
            f"{filtered_rate:.2%}",
            delta=f"{filtered_rate - test['taxa_alerta']:.2%}",
            delta_color="off",
            help=translate("overview.alert_rate_filtered_help", locale),
        )
    else:
        columns[3].metric(translate("overview.alert_rate", locale), f"{test['taxa_alerta']:.2%}")

    left, right = st.columns(2)
    left.subheader(translate("overview.shares", locale))
    left.dataframe(pd.DataFrame(metrics["proporcao_regimes"]).style.format("{:.1%}"))
    right.subheader(translate("overview.external", locale))
    right.dataframe(pd.DataFrame(metrics["concordancia_externa_teste"]).T.style.format("{:.3f}"))
    right.caption(translate("overview.external_note", locale))

    if not artifact_exists(RESULTS):
        return
    results = load_results()
    st.subheader(translate("overview.timeline", locale))
    split = st.selectbox(
        translate("overview.split", locale), ["validation", "test", "train"], index=1
    )
    window = results[results["split"] == split]
    figure = px.scatter(
        window,
        x="timestamp",
        y="usage_kwh",
        color="regime_name",
        symbol="is_anomaly",
        symbol_map={False: "circle", True: "x"},
        opacity=0.6,
    )
    figure.update_traces(marker={"size": 4})
    st.plotly_chart(figure, width="stretch")
    st.subheader(translate("overview.anomalies", locale))
    st.dataframe(
        window[window["is_anomaly"]].nlargest(20, "anomaly_score"),
        width="stretch",
        hide_index=True,
    )


def charts(locale: str) -> None:
    st.title(translate("charts.title", locale))
    tables = sorted((ARTIFACTS / "tables").glob("*.csv"))
    if not tables:
        st.info(translate("charts.no_tables", locale))
        return
    selected = st.selectbox(
        translate("charts.table", locale), tables, format_func=lambda path: path.stem
    )
    frame = pd.read_csv(selected)
    st.dataframe(frame, width="stretch", hide_index=True)
    numeric = frame.select_dtypes("number").columns.tolist()
    if len(numeric) >= 2:
        x_axis = st.selectbox(translate("charts.x_axis", locale), numeric, index=0)
        y_axis = st.selectbox(translate("charts.y_axis", locale), numeric, index=1)
        st.plotly_chart(px.scatter(frame, x=x_axis, y=y_axis), width="stretch")


def test_model(locale: str) -> None:
    st.title(translate("model.title", locale))
    model_available = artifact_exists("models/final_model.joblib")
    if not model_available:
        st.warning(translate("model.unavailable", locale))
    st.caption(translate("model.help", locale))
    uploaded = st.file_uploader(
        translate("model.upload", locale), type="csv", disabled=not model_available
    )
    if uploaded is None:
        return
    frame = pd.read_csv(uploaded)
    frame.columns = [snake_case(column) for column in frame.columns]
    try:
        prediction = store.model().predict(frame)
    except (ValueError, KeyError, TypeError, NotImplementedError) as error:
        st.error(translate("model.error", locale, error=error))
        return
    st.success(
        translate(
            "model.summary",
            locale,
            rows=len(prediction),
            anomalies=int(prediction["is_anomaly"].sum()),
        )
    )
    st.dataframe(prediction, width="stretch", hide_index=True)


PAGES = {"overview": overview, "charts": charts, "test_model": test_model}
st.sidebar.title("Steel Energy")
locale = st.sidebar.selectbox(
    translate("language", DEFAULT_LOCALE),
    SUPPORTED_LOCALES,
    format_func=LOCALE_LABELS.__getitem__,
    index=SUPPORTED_LOCALES.index(DEFAULT_LOCALE),
)
page = st.sidebar.radio(
    translate("nav.page", locale),
    PAGES,
    format_func=lambda page_key: translate(f"nav.{page_key}", locale),
    label_visibility="collapsed",
)
PAGES[page](locale)
