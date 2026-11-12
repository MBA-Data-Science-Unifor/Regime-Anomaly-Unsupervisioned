"""Streamlit shell that will consume, but never generate, project artifacts."""

from __future__ import annotations

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


def artifact_exists(relative: str) -> bool:
    return (ARTIFACTS / relative).exists()


def overview(locale: str) -> None:
    st.title(translate("overview.title", locale))
    st.caption(translate("overview.caption", locale))
    if not artifact_exists("metadata/final_metrics.json"):
        st.info(translate("overview.no_metrics", locale))
        return
    st.json(store.metrics())


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
    st.dataframe(frame, use_container_width=True, hide_index=True)
    numeric = frame.select_dtypes("number").columns.tolist()
    if len(numeric) >= 2:
        x_axis = st.selectbox(translate("charts.x_axis", locale), numeric, index=0)
        y_axis = st.selectbox(translate("charts.y_axis", locale), numeric, index=1)
        st.plotly_chart(px.scatter(frame, x=x_axis, y=y_axis), use_container_width=True)


def test_model(locale: str) -> None:
    st.title(translate("model.title", locale))
    model_available = artifact_exists("models/final_model.joblib")
    if not model_available:
        st.warning(translate("model.unavailable", locale))
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
    st.dataframe(prediction, use_container_width=True, hide_index=True)


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
