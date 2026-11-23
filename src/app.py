"""Streamlit shell that will consume, but never generate, project artifacts."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from regime_anomaly.data import snake_case, load_preprocessor, load_data, DEFAULT_DATASET
from regime_anomaly import (
    ARTIFACTS,
    DEFAULT_LOCALE,
    LOCALE_LABELS,
    SUPPORTED_LOCALES,
    ArtifactStore,
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
    try:
        prediction = store.model().predict(frame)
    except (ValueError, KeyError, TypeError, NotImplementedError) as error:
        st.error(translate("model.error", locale, error=error))
        return
    st.dataframe(prediction, use_container_width=True, hide_index=True)



def preprocessing(locale: str) -> None:
    st.title(translate("prep.title", locale))
    st.caption(translate("prep.caption", locale))

    if not (
        artifact_exists("metadata/preprocessing.json")
        and artifact_exists("models/preprocessor.joblib")
    ):
        st.info(translate("prep.unavailable", locale))
        return

    meta = store.describe_metadata()

    # 1) Resumo do JSON
    metrics = st.columns(4)
    metrics[0].metric(translate("prep.rows_train", locale), f"{meta['n_train']:,}")
    metrics[1].metric(translate("prep.rows_test", locale), f"{meta['n_test']:,}")
    metrics[2].metric(translate("prep.n_components", locale), len(meta["pca_components"]))
    metrics[3].metric(translate("prep.variance", locale), f"{meta['cumulative_variance'][-1]:.1%}")

    # 2) Elaboração dos Gráficos
    figure = go.Figure()
    
    figure.add_bar(
        x=meta["pca_components"], y=meta["explained_variance_ratio"], 
        name=translate("prep.individual", locale)
    )
    
    figure.add_scatter(
        x=meta["pca_components"], y=meta["cumulative_variance"],
        name=translate("prep.cumulative", locale)
    )
    
    figure.update_layout(title=translate("prep.variance_chart", locale), yaxis_tickformat=".0%")
    st.plotly_chart(figure, use_container_width=True)
    
    with st.expander(translate("prep.features", locale)):

        groups = pd.DataFrame(
            {
                translate("prep.group", locale): [
                    translate("prep.group.numeric", locale),
                    translate("prep.group.categorical", locale),
                    translate("prep.group.reported", locale),
                    translate("prep.group.deleted", locale),
                ],
                
                translate("prep.columns", locale): [
                    ", ".join(meta["feature_numeric"]),
                    ", ".join(meta["one_hot_features"]),
                    ", ".join(meta["feature_reporting_only"]),
                    ", ".join(meta["feature_deleted"]),
                ],
            }
        )

    st.dataframe(groups, use_container_width=True, hide_index=True)

    # 3) Interação
    st.subheader(translate("prep.try", locale))
    uploaded = st.file_uploader(translate("prep.upload", locale), type="csv", key="prep_upload")
    
    if uploaded is not None:
        frame = pd.read_csv(uploaded)
    elif DEFAULT_DATASET.exists():
        sample_rows = 500
        frame = load_data().head(sample_rows)
        st.caption(translate("prep.sample_caption", locale, rows=sample_rows))
    else:
        st.info(translate("prep.no_input", locale))
        return
    
    frame.columns = [snake_case(column) for column in frame.columns]
    missing = [column for column in meta["required_columns"] if column not in frame.columns]
    if missing:
        st.error(translate("prep.missing", locale, columns=", ".join(missing)))
        return
    try:
        transformed = load_preprocessor().transform(frame)
    except (ValueError, KeyError, TypeError) as error:
        st.error(translate("prep.error", locale, error=error))
        return
    
    processed = pd.DataFrame(transformed, columns=meta["pca_components"], index=frame.index)
    before, after = st.columns(2)
    before.caption(translate("prep.before", locale))
    before.dataframe(frame[meta["required_columns"]].head(200), use_container_width=True)
    after.caption(translate("prep.after", locale))
    after.dataframe(processed.head(200), use_container_width=True)
    
    if processed.shape[1] >= 2:
        plot = processed.copy()
        label = "load_type"
        if label in frame.columns:
            plot[label] = frame[label].astype(str)
        st.plotly_chart(
            px.scatter(plot, x="PC1", y="PC2", color=label if label in plot else None),
            use_container_width=True,
        )


PAGES = {"overview": overview, "charts": charts, 
         "preprocessing": preprocessing, "test_model": test_model}

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
