"""Read-only Streamlit dashboard for energy regimes and anomaly monitoring."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from regime_anomaly.artifacts import ArtifactStore
from regime_anomaly.dashboard import (
    DISPLAY_COLUMNS,
    PREPROCESSING_PATH,
    alert_severity,
    artifact_status,
    available_measurements,
    load_metrics,
    load_preprocessing_data,
    load_results,
    metrics_version,
    results_version,
)
from regime_anomaly.i18n import DEFAULT_LOCALE, translate

st.set_page_config(page_title="Monitoramento de energia", page_icon="⚡", layout="wide")


@st.cache_data(show_spinner=False)
def cached_results(version: int) -> pd.DataFrame:
    return load_results(version)


@st.cache_data(show_spinner=False)
def cached_metrics(version: int) -> dict[str, object]:
    return load_metrics()


def results() -> pd.DataFrame:
    return cached_results(results_version())


def missing_artifacts() -> None:
    names = {
        "results": "resultados processados",
        "metrics": "métricas finais",
        "model": "modelo final",
        "preprocessor": "pré-processador",
    }
    missing = [names[key] for key, present in artifact_status().items() if not present]
    if missing:
        st.info("Dashboard em modo de preparação. Artefatos ausentes: " + ", ".join(missing) + ".")


def period_filter(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "timestamp" not in frame:
        return frame
    first, last = frame["timestamp"].min(), frame["timestamp"].max()
    picked = st.sidebar.date_input(
        "Período analisado", (first.date(), last.date()), first.date(), last.date()
    )
    if isinstance(picked, tuple) and len(picked) == 2:
        return frame[
            frame["timestamp"].between(
                pd.Timestamp(picked[0]),
                pd.Timestamp(picked[1]) + timedelta(days=1),
                inclusive="left",
            )
        ]
    return frame


def overview(frame: pd.DataFrame) -> None:
    st.title("Central de monitoramento energético")
    st.caption(
        "Demonstração com dados históricos publicados; não representa telemetria industrial ao vivo."
    )
    missing_artifacts()
    if frame.empty:
        st.write(
            "Publique `artifacts/data/processed/analysis_results.csv` para preencher o monitoramento automaticamente."
        )
        return
    severity = alert_severity(frame)
    latest = frame.iloc[-1]
    cards = st.columns(4)
    cards[0].metric("Estado atual", severity.iloc[-1])
    cards[1].metric("Última medição", latest["timestamp"].strftime("%d/%m/%Y %H:%M"))
    cards[2].metric("Alertas no período", int((severity != "Normal").sum()))
    cards[3].metric(
        "Consumo atual (kWh)",
        f"{latest['energy_consumption_kwh']:.2f}"
        if "energy_consumption_kwh" in latest
        else "Indisponível",
    )
    measurements = available_measurements(frame)
    if measurements:
        metric = measurements[0]
        figure = px.line(
            frame,
            x="timestamp",
            y=metric,
            labels={"timestamp": "Data e hora", metric: DISPLAY_COLUMNS[metric]},
        )
        alerts = frame.loc[severity != "Normal"]
        if not alerts.empty:
            figure.add_scatter(
                x=alerts["timestamp"],
                y=alerts[metric],
                mode="markers",
                name="Alerta",
                marker={"color": "#D55E00", "size": 9},
            )
        st.plotly_chart(figure, use_container_width=True)


def monitoring(frame: pd.DataFrame) -> None:
    st.title("Monitoramento temporal")
    st.caption(
        "A atualização lê novamente os resultados publicados; a interface nunca treina modelos."
    )
    if frame.empty:
        missing_artifacts()
        return
    measurements = available_measurements(frame)
    if not measurements:
        st.warning("Não há medidas numéricas reconhecidas para visualização.")
        return
    metric = st.selectbox("Métrica", measurements, format_func=lambda name: DISPLAY_COLUMNS[name])
    data = frame.assign(severidade=alert_severity(frame))
    figure = px.line(
        data,
        x="timestamp",
        y=metric,
        color="severidade",
        labels={
            "timestamp": "Data e hora",
            metric: DISPLAY_COLUMNS[metric],
            "severidade": "Estado",
        },
        color_discrete_map={"Normal": "#009E73", "Atenção": "#E69F00", "Crítico": "#D55E00"},
    )
    st.plotly_chart(figure, use_container_width=True)
    st.dataframe(data.tail(100), use_container_width=True, hide_index=True)


def alerts(frame: pd.DataFrame) -> None:
    st.title("Central de alertas")
    if frame.empty:
        missing_artifacts()
        return
    data = frame.assign(alert_severity=alert_severity(frame))
    choices = st.multiselect(
        "Severidade",
        sorted(data.alert_severity.unique()),
        default=[item for item in ("Atenção", "Crítico") if item in set(data.alert_severity)],
    )
    filtered = data[data.alert_severity.isin(choices)]
    if filtered.empty:
        st.success("Não há alertas para os filtros selecionados.")
        return
    columns = [
        name
        for name in [
            "timestamp",
            "alert_severity",
            "anomaly_score",
            "alert_reason",
            "supervised_load_type",
            "cluster_operational_profile",
            "energy_consumption_kwh",
        ]
        if name in filtered
    ]
    st.dataframe(filtered[columns], use_container_width=True, hide_index=True)
    st.download_button(
        "Baixar alertas em CSV",
        filtered.to_csv(index=False).encode("utf-8-sig"),
        "alertas.csv",
        "text/csv",
    )


def models(_: pd.DataFrame) -> None:
    st.title("Modelos e qualidade")
    metrics = cached_metrics(metrics_version())
    if metrics:
        st.json(metrics)
    else:
        st.info("As métricas aparecerão após a publicação de `metadata/final_metrics.json`.")


def reports(frame: pd.DataFrame) -> None:
    st.title("Relatório operacional")
    if frame.empty:
        missing_artifacts()
        return
    severity = alert_severity(frame)
    report = pd.DataFrame(
        {
            "Início do período": [frame.timestamp.min()],
            "Fim do período": [frame.timestamp.max()],
            "Medições analisadas": [len(frame)],
            "Alertas": [int((severity != "Normal").sum())],
            "Alertas críticos": [int((severity == "Crítico").sum())],
        }
    )
    st.dataframe(report, use_container_width=True, hide_index=True)
    st.download_button(
        "Baixar resumo em CSV",
        report.to_csv(index=False).encode("utf-8-sig"),
        "relatorio_operacional.csv",
        "text/csv",
    )
    st.caption(
        "Alertas apoiam investigação operacional; não são diagnósticos de falha ou ordens de manutenção."
    )


@st.cache_data(show_spinner=False)
def cache_preprocessing(version: int):
    return load_preprocessing_data()


def preprocessing(_: pd.DataFrame) -> None:
    st.title("Preparação dos dados")

    version = PREPROCESSING_PATH.stat().st_mtime_ns if PREPROCESSING_PATH.exists() else 0
    meta = cache_preprocessing(version)
    if not meta:
        st.info("Execute o notebook 02 para publicar `metadata/preprocessed_data.json`.")
        return

    st.caption(f"Configuração escolhida: {meta['chosen_config']}")
    cards = st.columns(3)
    cards[0].metric("Linhas de treino", meta["n_train"])
    cards[1].metric("Linhas de teste", meta["n_test"])
    cards[2].metric("Componentes PCA", len(meta["pca_components"]))

    st.write(
        f"Divisão temporal: treino de {meta['train_date_range'][0][:10]} "
        f"a {meta['train_date_range'][1][:10]}; teste até {meta['test_date_range'][1][:10]}."
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Entram no modelo")
        st.write("Numéricas (padronizadas):", ", ".join(meta["feature_numeric"]))
        st.write("Categóricas (one-hot):", ", ".join(meta["feature_categoric"]))
    with right:
        st.subheader("Ficam de fora")
        st.write("Só para validar clusters:", ", ".join(meta["feature_reporting_only"]))
        st.write("Removidas:", ", ".join(meta["feature_deleted"]))

    st.subheader("Variância explicada pelo PCA")
    pca = pd.DataFrame(
        {
            "Componente": meta["pca_components"],
            "Variância acumulada (%)": [round(v * 100, 1) for v in meta["cumulative_variance"]],
        }
    )
    st.plotly_chart(
        px.bar(pca, x="Componente", y="Variância acumulada (%)"), use_container_width=True
    )


def test_model(_: pd.DataFrame) -> None:
    """Run the published model on an uploaded CSV in the UCI layout (never retrains)."""
    st.title(translate("model.title", DEFAULT_LOCALE))
    available = artifact_status()["model"]
    if not available:
        st.warning(translate("model.unavailable", DEFAULT_LOCALE))
    st.caption(translate("model.help", DEFAULT_LOCALE))
    uploaded = st.file_uploader(
        translate("model.upload", DEFAULT_LOCALE), type="csv", disabled=not available
    )
    if uploaded is None:
        return
    try:
        prediction = ArtifactStore().model().predict(pd.read_csv(uploaded))
    except (ValueError, KeyError, TypeError, NotImplementedError) as error:
        st.error(translate("model.error", DEFAULT_LOCALE, error=error))
        return
    st.success(
        translate(
            "model.summary",
            DEFAULT_LOCALE,
            rows=len(prediction),
            anomalies=int(prediction["is_anomaly"].sum()),
        )
    )
    st.dataframe(prediction, width="stretch", hide_index=True)


PAGES = {
    "Visão geral": overview,
    "Monitoramento": monitoring,
    "Alertas": alerts,
    "Modelos": models,
    "Preparação": preprocessing,
    "Relatórios": reports,
    "Testar modelo": test_model,
}

st.sidebar.title("⚡ Steel Energy")
st.sidebar.caption("Regimes operacionais e anomalias")
if st.sidebar.button("Atualizar dados", use_container_width=True):
    cached_results.clear()
    cached_metrics.clear()
    st.rerun()
st.sidebar.caption("Use este botão após o pipeline publicar novos artefatos.")
selected_page = st.sidebar.radio("Navegação", list(PAGES))
PAGES[selected_page](period_filter(results()))
