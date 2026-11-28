"""Dashboard histórico: consumo, regimes, anomalias e cenários controlados."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from regime_anomaly import preprocessing as pp
from regime_anomaly.artifacts import ArtifactStore
from regime_anomaly.dashboard import (
    PREPARED_PATH,
    alert_masks,
    alert_severity,
    artifact_versions,
    audit_artifacts,
    daily_alert_counts,
    load_metrics,
    load_preprocessing_data,
    load_results,
)
from regime_anomaly.scenarios import anomaly_scenarios

st.set_page_config(page_title="Steel Energy | Monitoramento", page_icon="⚡", layout="wide")

st.markdown(
    """<style>
    .stApp {background: #11142d; color: #e8edf8;}
    [data-testid="stSidebar"] {background: #161b38;}
    [data-testid="stMainBlockContainer"] {padding-top: 2rem; max-width: 1700px;}
    div[data-testid="stMetric"] {background: #20284b; border: 1px solid #303c62;
        border-radius: 14px; padding: 18px 20px; min-height: 110px;}
    div[data-testid="stMetricLabel"] {color: #aebcda;}
    div[data-testid="stMetricValue"] {color: #f5f7ff; font-weight: 700;}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {background: #1c2444;
        border: 1px solid #303c62; border-radius: 14px;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px; border-bottom: 1px solid #303c62;}
    .stTabs [data-baseweb="tab"] {padding: 12px 16px; color: #abbadc;}
    .stTabs [aria-selected="true"] {color: #71decc;}
    .eyebrow {font-size: .74rem; color: #71decc; letter-spacing: .16em; font-weight: 700;}
    .subtitle {color: #aebcda; margin-top: -.45rem;}
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def cached_audit(versions: tuple[int, ...]) -> pd.DataFrame:
    return audit_artifacts()


@st.cache_data(show_spinner=False)
def cached_results(version: int) -> pd.DataFrame:
    return load_results(version)


@st.cache_data(show_spinner=False)
def cached_metrics(version: int) -> dict:
    return load_metrics()


@st.cache_data(show_spinner=False)
def cached_preprocessing(version: int) -> dict:
    return load_preprocessing_data()


@st.cache_data(show_spinner=False)
def cached_prepared(version: int) -> pd.DataFrame:
    frame = pd.read_csv(PREPARED_PATH, parse_dates=[pp.TIMESTAMP_COLUMN])
    return frame


@st.fragment(run_every="30s")
def refresh_when_artifacts_change() -> None:
    current = artifact_versions()
    previous = st.session_state.get("artifact_versions")
    st.session_state["artifact_versions"] = current
    if previous is not None and current != previous:
        st.session_state.pop("scenario_results", None)
        st.rerun(scope="app")


def usable(audit: pd.DataFrame, *names: str) -> bool:
    statuses = audit.set_index("Artefato")["Integridade"]
    return all(statuses.get(name) in ("Íntegro", "Não verificado") for name in names)


def status_warning(audit: pd.DataFrame, *names: str) -> None:
    relevant = audit[audit["Artefato"].isin(names)]
    unavailable = relevant[
        relevant["Integridade"].isin(
            ["Ausente", "Divergente", "Indisponível", "Proveniência divergente"]
        )
    ]
    if not unavailable.empty:
        st.warning(
            "Artefatos indisponíveis ou divergentes: "
            + ", ".join(unavailable["Artefato"])
            + ". Consulte a aba Artefatos."
        )
    elif (relevant["Integridade"] == "Não verificado").any():
        st.warning(
            "Integridade não verificada: o manifesto não contém todos os artefatos desta seção."
        )


def plot_style(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cbd5ea",
        margin={"l": 12, "r": 12, "t": 30, "b": 10},
        legend_title_text="",
        colorway=["#59d8c3", "#8c9aff", "#ffad74", "#f37284"],
    )
    fig.update_xaxes(gridcolor="#34405e")
    fig.update_yaxes(gridcolor="#34405e")
    return fig


def period_filter(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "timestamp" not in frame:
        return frame
    first, last = frame["timestamp"].min(), frame["timestamp"].max()
    picked = st.sidebar.date_input(
        "Período histórico", (first.date(), last.date()), first.date(), last.date()
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
    if frame.empty:
        st.info("Não há resultados disponíveis no período selecionado.")
        return
    severity = alert_severity(frame)
    alert_count = int((severity == "Atenção").sum() + (severity == "Crítico").sum())
    classified_count = int(severity.isin(["Normal", "Atenção", "Crítico"]).sum())
    cards = st.columns(4)
    cards[0].metric("Leituras no período", f"{len(frame):,}".replace(",", "."))
    cards[1].metric(
        "Alertas filtrados", f"{alert_count:,}".replace(",", ".") if classified_count else "—"
    )
    cards[2].metric(
        "Taxa de alertas",
        f"{100 * alert_count / classified_count:.2f}%" if classified_count else "—",
    )
    consumption = frame.get("energy_consumption_kwh")
    cards[3].metric(
        "Consumo médio / leitura",
        f"{consumption.mean():.2f} kWh" if consumption is not None else "Indisponível",
    )
    left, right = st.columns([2.1, 1])
    with left, st.container(border=True):
        st.subheader("Consumo ao longo do período")
        st.caption("Média diária das leituras de 15 minutos · dados históricos")
        if consumption is not None:
            daily = (
                frame.set_index("timestamp")["energy_consumption_kwh"]
                .resample("D")
                .mean()
                .dropna()
                .reset_index()
            )
            fig = px.line(
                daily,
                x="timestamp",
                y="energy_consumption_kwh",
                labels={"timestamp": "Data", "energy_consumption_kwh": "Média por leitura (kWh)"},
            )
            daily_counts = daily_alert_counts(frame)
            daily = daily.merge(daily_counts, on="timestamp", how="left")
            highlighted = daily[(daily["Mantidos"] > 0) | (daily["Suprimidos"] > 0)]
            if not highlighted.empty:
                fig.add_scatter(
                    x=highlighted["timestamp"],
                    y=highlighted["energy_consumption_kwh"],
                    mode="markers",
                    name="Dia com alertas brutos",
                    customdata=highlighted[["Mantidos", "Suprimidos"]].to_numpy(),
                    hovertemplate="Data: %{x|%d/%m/%Y}<br>Média diária: %{y:.2f} kWh<br>Mantidos: %{customdata[0]}<br>Suprimidos: %{customdata[1]}<extra></extra>",
                    marker={
                        "color": "#ff677d",
                        "size": 10,
                        "symbol": "diamond",
                        "line": {"color": "white", "width": 1.5},
                    },
                )
            st.plotly_chart(plot_style(fig), width="stretch")
            st.caption(
                "Losangos indicam dias com alertas brutos; a posição vertical é a média diária, não a leitura individual."
            )
    with right, st.container(border=True):
        st.subheader("Composição dos regimes")
        st.caption("Distribuição das leituras no período")
        if "cluster_operational_profile" in frame:
            shares = (
                frame["cluster_operational_profile"]
                .value_counts()
                .rename_axis("Regime")
                .reset_index(name="Leituras")
            )
            fig = px.pie(
                shares,
                names="Regime",
                values="Leituras",
                hole=0.65,
                color_discrete_sequence=["#59d8c3", "#8c9aff", "#ffad74"],
            )
            st.plotly_chart(plot_style(fig), width="stretch")
        else:
            st.info("Os resultados não incluem nomes de regimes.")
    st.caption("Alertas indicam leituras incomuns para investigação; não são falhas confirmadas.")
    if classified_count < len(frame):
        st.caption(
            f"{len(frame) - classified_count} leituras sem classificação foram excluídas da taxa de alertas."
        )
    report = pd.DataFrame(
        {
            "leituras": [len(frame)],
            "leituras_classificadas": [classified_count],
            "alertas_filtrados": [alert_count if classified_count else None],
            "inicio": [frame.timestamp.min()],
            "fim": [frame.timestamp.max()],
        }
    )
    st.download_button(
        "Baixar resumo do período",
        report.to_csv(index=False).encode("utf-8-sig"),
        "resumo_periodo.csv",
        "text/csv",
    )


def monitoring(frame: pd.DataFrame) -> None:
    st.subheader("Monitoramento temporal")
    if frame.empty:
        st.info("Sem dados para o período selecionado.")
        return
    choices = {
        "Consumo (kWh)": "energy_consumption_kwh",
        "Energia reativa atrasada (kvarh)": "lagging_reactive_energy_kvarh",
        "Energia reativa adiantada (kvarh)": "leading_reactive_energy_kvarh",
        "Escore de anomalia": "anomaly_score",
    }
    choices = {label: col for label, col in choices.items() if col in frame}
    if not choices:
        st.info("Nenhuma medida reconhecida foi encontrada.")
        return
    first_day = frame["timestamp"].min().date()
    last_day = frame["timestamp"].max().date()
    initial_start = max(first_day, last_day - timedelta(days=6))
    selected = st.date_input(
        "Janela detalhada do monitoramento",
        value=(initial_start, last_day),
        min_value=first_day,
        max_value=last_day,
        key=f"monitor_window_{first_day}_{last_day}",
        help="A janela inicial mostra os últimos sete dias do período selecionado na barra lateral.",
    )
    if not isinstance(selected, tuple) or len(selected) != 2:
        st.info("Selecione as datas inicial e final para visualizar o gráfico.")
        return
    data = frame.loc[
        frame["timestamp"].between(
            pd.Timestamp(selected[0]),
            pd.Timestamp(selected[1]) + timedelta(days=1),
            inclusive="left",
        )
    ].copy()
    if data.empty:
        st.info("Não há leituras nessa janela. Escolha outro período.")
        return
    label = st.selectbox("Medida", list(choices))
    kept, suppressed = alert_masks(data)
    show = st.multiselect(
        "Destacar no gráfico", ["Mantidos", "Suprimidos"], default=["Mantidos", "Suprimidos"]
    )
    only_alerts = st.toggle("Exibir somente alertas", value=False)
    st.caption(
        f"Janela: {selected[0]:%d/%m/%Y} a {selected[1]:%d/%m/%Y} · "
        f"{len(data):,} leituras · {int(kept.sum())} alertas mantidos · {int(suppressed.sum())} suprimidos."
    )
    with st.container(border=True):
        long_window = (selected[1] - selected[0]).days >= 14
        if long_window:
            line_data = (
                data.set_index("timestamp")[[choices[label]]]
                .resample("h")
                .mean()
                .dropna()
                .reset_index()
            )
        else:
            line_data = data
        fig = px.line(
            line_data,
            x="timestamp",
            y=choices[label],
            labels={"timestamp": "Data e hora", choices[label]: label},
            render_mode="svg",
        )
        fig.update_traces(
            line={"color": "rgba(127, 164, 196, 0.35)", "width": 1},
            visible=not only_alerts,
            name="Média horária" if long_window else "Leituras",
        )
        for name, mask, color, symbol in (
            ("Mantidos", kept, "#ff657c", "triangle-up"),
            ("Suprimidos", suppressed, "#ffcb70", "circle"),
        ):
            alerts = data.loc[mask]
            if name not in show or alerts.empty:
                continue
            fig.add_scatter(
                x=alerts["timestamp"],
                y=alerts[choices[label]],
                mode="markers",
                name=f"Alertas {name.lower()}",
                marker={
                    "color": color,
                    "size": 14,
                    "symbol": symbol,
                    "line": {"color": "#11142d", "width": 2},
                },
                hovertemplate=f"{name}<br>Data: %{{x|%d/%m/%Y %H:%M}}<br>{label}: %{{y:.3f}}<extra></extra>",
            )
        st.plotly_chart(plot_style(fig), width="stretch")
        st.caption(
            "Triângulo vermelho: alerta mantido. Círculo amarelo: alerta bruto suprimido pelo filtro. "
            + (
                "Linha: média horária; pontos: leituras individuais."
                if long_window
                else "Linha: leituras individuais de 15 minutos."
            )
        )
        if not any(
            (name in show and bool(mask.any()))
            for name, mask in (("Mantidos", kept), ("Suprimidos", suppressed))
        ):
            st.info(
                "Nenhum alerta das categorias selecionadas nesta janela. Amplie o período ou ajuste os tipos destacados."
            )
    st.dataframe(data.tail(100), width="stretch", hide_index=True)


def alerts_view(frame: pd.DataFrame) -> None:
    st.subheader("Alertas e transições")
    st.caption("Compare os alertas antes e depois do filtro. Fronteira não é sinônimo de falha.")
    if frame.empty or "is_anomaly_raw" not in frame or "is_anomaly" not in frame:
        st.info("Os resultados com indicadores bruto e filtrado ainda não estão disponíveis.")
        return
    raw = frame["is_anomaly_raw"].fillna(False).astype(bool)
    filtered, suppressed = alert_masks(frame)
    cards = st.columns(3)
    cards[0].metric("Alertas brutos", int(raw.sum()))
    cards[1].metric("Alertas mantidos", int(filtered.sum()))
    cards[2].metric("Suprimidos pelo filtro", int(suppressed.sum()))
    counts = daily_alert_counts(frame)
    daily_long = counts.melt(
        id_vars="timestamp",
        value_vars=["Mantidos", "Suprimidos"],
        var_name="Situação",
        value_name="Alertas",
    )
    with st.container(border=True):
        st.markdown("#### Alertas por dia")
        st.caption(
            "Contagem diária por situação; o filtro separa os alertas brutos em mantidos e suprimidos."
        )
        fig = px.bar(
            daily_long,
            x="timestamp",
            y="Alertas",
            color="Situação",
            color_discrete_map={"Mantidos": "#ff657c", "Suprimidos": "#ffcb70"},
            labels={"timestamp": "Data"},
        )
        st.plotly_chart(plot_style(fig), width="stretch")
    mode = st.radio("Exibir", ["Mantidos", "Brutos", "Suprimidos"], horizontal=True)
    mask = {"Mantidos": filtered, "Brutos": raw, "Suprimidos": suppressed}[mode]
    columns = [
        c
        for c in (
            "timestamp",
            "cluster_operational_profile",
            "energy_consumption_kwh",
            "anomaly_score",
            "regime_boundary",
            "is_anomaly_raw",
            "is_anomaly",
            "reference_load_type",
        )
        if c in frame
    ]
    selected = frame.loc[mask, columns].sort_values("timestamp", ascending=False)
    st.dataframe(selected, width="stretch", hide_index=True)
    st.download_button(
        "Baixar seleção em CSV",
        selected.to_csv(index=False).encode("utf-8-sig"),
        "alertas.csv",
        "text/csv",
    )


def models_view(metrics: dict) -> None:
    st.subheader("Modelos e avaliação")
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.markdown("#### K-Means · regimes")
        st.write(
            "Agrupa leituras por assinatura elétrica em três perfis. Os nomes precisam de confirmação operacional."
        )
        val = metrics.get("validacao", {})
        test = metrics.get("teste", {})
        a, b = st.columns(2)
        a.metric("Silhueta · validação", f"{val['silhouette']:.3f}" if "silhouette" in val else "—")
        b.metric("Silhueta · teste", f"{test['silhouette']:.3f}" if "silhouette" in test else "—")
    with right, st.container(border=True):
        st.markdown("#### Isolation Forest · atipicidade")
        st.write(
            "Sinaliza leituras incomuns em relação ao treino. O limiar não mede a probabilidade de falha."
        )
        anomaly = metrics.get("anomalia", {})
        a, b = st.columns(2)
        a.metric("Limiar de escore", f"{anomaly['limiar']:.4f}" if "limiar" in anomaly else "—")
        b.metric(
            "Meta bruta · validação",
            f"{100 * anomaly['taxa_alerta_premissa']:.1f}%"
            if "taxa_alerta_premissa" in anomaly
            else "—",
        )
    with st.container(border=True):
        st.markdown("#### KNN supervisionado · `Load_Type`")
        st.write(
            "Experimento do notebook 03, usado para comparar as classes conhecidas após a medição. Não está publicado para inferência neste painel. GMM e Extra Trees são alternativas experimentais."
        )
        st.caption(
            "O teste é retrospectivo: a EDA já examinou o ano inteiro. Não há rótulos de falha para medir a precisão do Isolation Forest."
        )
    with st.expander("Métricas publicadas pelo notebook 03"):
        st.json(metrics or {})


def scenario_view(audit: pd.DataFrame, versions: tuple[int, ...]) -> None:
    st.subheader("Laboratório de cenários")
    st.caption(
        "Modifique uma leitura de validação e compare o escore com o limiar; os vizinhos permanecem iguais."
    )
    st.warning(
        "Simulação de sensibilidade: combinações artificiais podem não ser fisicamente possíveis e não são falhas confirmadas."
    )
    status_warning(audit, "Base preparada", "Preparação", "Modelo")
    if not usable(audit, "Base preparada", "Preparação", "Modelo"):
        return
    try:
        prepared = cached_prepared(versions[4])
        validation = prepared.loc[prepared[pp.SPLIT_COLUMN] == "validation"]
        days = sorted((validation[pp.TIMESTAMP_COLUMN] - pp.EXPECTED_FREQUENCY).dt.date.unique())
        if not days:
            st.info("A base preparada não contém validação.")
            return
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Não foi possível ler a base preparada do notebook 02: {error}")
        return
    with st.form("scenario_form"):
        day = st.selectbox(
            "Dia de referência · validação", days, format_func=lambda d: d.strftime("%d/%m/%Y")
        )
        a, b, c = st.columns(3)
        usage = a.number_input("Consumo (kWh)", min_value=0.0, value=150.0, step=10.0)
        reactive = b.number_input("Reativa adiantada (kvarh)", min_value=0.0, value=50.0, step=5.0)
        factor = c.number_input(
            "Fator de potência atrasado (%)", min_value=0.0, max_value=100.0, value=5.0
        )
        submit = st.form_submit_button("Executar simulação", type="primary")
    if submit:
        try:
            bundle = ArtifactStore().model()
            output = anomaly_scenarios(
                bundle,
                prepared,
                day=day,
                custom={pp.USAGE: usage, pp.LEADING_KVARH: reactive, pp.LAGGING_PF: factor},
            )
            st.session_state["scenario_results"] = (output, bundle.anomaly_threshold)
        except (OSError, ValueError, KeyError, TypeError) as error:
            st.error(f"Não foi possível simular: {error}")
    if "scenario_results" in st.session_state:
        output, threshold = st.session_state["scenario_results"]
        a, b, c = st.columns(3)
        a.metric("Limiar do modelo", f"{threshold:.4f}")
        b.metric("Cenários com alerta bruto", int(output["alerta_bruto"].sum()))
        c.metric("Cenários com alerta filtrado", int(output["alerta_filtrado"].sum()))
        with st.container(border=True):
            fig = px.bar(
                output,
                x="escore",
                y="cenario",
                orientation="h",
                color="alerta_bruto",
                color_discrete_map={True: "#f37284", False: "#59d8c3"},
                labels={
                    "escore": "Escore de atipicidade",
                    "cenario": "Cenário",
                    "alerta_bruto": "Alerta bruto",
                },
            )
            fig.add_vline(x=threshold, line_dash="dash", line_color="#f4cb67")
            st.plotly_chart(plot_style(fig), width="stretch")
        st.caption(
            "Linha tracejada: limiar. O filtro pode suprimir o alerta se a leitura alterada gerar uma fronteira."
        )
        st.dataframe(output, width="stretch", hide_index=True)
        st.download_button(
            "Baixar cenários em CSV",
            output.to_csv(index=False).encode("utf-8-sig"),
            "cenarios.csv",
            "text/csv",
        )


def artifacts_view(audit: pd.DataFrame, versions: tuple[int, ...]) -> None:
    st.subheader("Origem e integridade")
    st.caption(
        "SHA-256 comparado ao manifesto publicado. 'Não verificado' indica ausência de referência no manifesto."
    )
    st.dataframe(audit, width="stretch", hide_index=True)
    status_warning(audit, "Preparação")
    if usable(audit, "Preparação"):
        try:
            meta = cached_preprocessing(versions[3])
            counts = meta.get("particoes", {}).get("linhas", {})
            st.markdown("#### Preparação · notebook 02")
            a, b, c = st.columns(3)
            a.metric("Treino", f"{counts.get('train', 0):,}")
            b.metric("Validação", f"{counts.get('validation', 0):,}")
            c.metric("Teste", f"{counts.get('test', 0):,}")
            with st.expander("Transformações e conjuntos de variáveis"):
                st.json(
                    {
                        "transformacoes": meta.get("transformacoes", {}),
                        "features": meta.get("conjuntos_de_features", {}),
                        "excluidas": meta.get("excluidas", {}),
                    }
                )
        except (OSError, ValueError, TypeError, KeyError) as error:
            st.error(f"Não foi possível ler os metadados do notebook 02: {error}")
    st.markdown("#### Aplicar modelo publicado a um CSV")
    st.caption(
        "Use as colunas da base UCI; `Load_Type`, se presente, é ignorado. O modelo não é reajustado."
    )
    status_warning(audit, "Modelo")
    upload = st.file_uploader("Arquivo CSV", type="csv", disabled=not usable(audit, "Modelo"))
    if upload is not None:
        try:
            prediction = ArtifactStore().model().predict(pd.read_csv(upload))
            st.dataframe(prediction, width="stretch", hide_index=True)
        except (OSError, ValueError, KeyError, TypeError, NotImplementedError) as error:
            st.error(f"Não foi possível aplicar o modelo: {error}")


st.sidebar.markdown("## ⚡ STEEL ENERGY")
st.sidebar.caption("ENERGIA · REGIMES · ANOMALIAS")
st.sidebar.divider()
st.sidebar.caption("Dados históricos · atualização verificada a cada 30 segundos")
if st.sidebar.button("Atualizar dados", width="stretch"):
    st.cache_data.clear()
    st.session_state.pop("scenario_results", None)
    st.rerun()
refresh_when_artifacts_change()
versions = artifact_versions()
audit = cached_audit(versions)
st.markdown('<div class="eyebrow">STEEL ENERGY / ANÁLISE OPERACIONAL</div>', unsafe_allow_html=True)
st.title("Visão energética")
st.markdown(
    '<div class="subtitle">Regimes, leituras incomuns e simulações em um só lugar.</div>',
    unsafe_allow_html=True,
)
st.caption("Base histórica de 2018 · demonstração, não telemetria ao vivo")
status_warning(audit, "Resultados")
try:
    frame = cached_results(versions[0]) if usable(audit, "Resultados") else pd.DataFrame()
    frame = period_filter(frame)
except (OSError, ValueError, KeyError) as error:
    st.error(f"Não foi possível ler os resultados do notebook 03: {error}")
    frame = pd.DataFrame()
try:
    metrics = cached_metrics(versions[1]) if usable(audit, "Métricas") else {}
except (OSError, ValueError, TypeError):
    metrics = {}
tabs = st.tabs(["Visão geral", "Monitoramento", "Alertas", "Modelos", "Cenários", "Artefatos"])
with tabs[0]:
    overview(frame)
with tabs[1]:
    monitoring(frame)
with tabs[2]:
    alerts_view(frame)
with tabs[3]:
    status_warning(audit, "Métricas")
    models_view(metrics)
with tabs[4]:
    scenario_view(audit, versions)
with tabs[5]:
    artifacts_view(audit, versions)
