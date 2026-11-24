"""Generate compact, versionable figures used by the MkDocs evidence pages."""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "artifacts" / "data" / "raw" / "Steel_industry_data.csv"
NOTEBOOKS = ROOT / "artifacts" / "notebooks"
OUTPUT = ROOT / "docs" / "assets" / "images"

PALETTE = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
}


def notebook_output(notebook: Path, cell_index: int) -> str:
    """Return the plain-text and stream output stored for one notebook cell."""
    document = json.loads(notebook.read_text(encoding="utf-8"))
    texts: list[str] = []
    for output in document["cells"][cell_index].get("outputs", []):
        if output.get("output_type") == "stream":
            value = output.get("text", "")
        else:
            value = output.get("data", {}).get("text/plain", "")
        texts.extend(value if isinstance(value, list) else [value])
    return "".join(texts)


def save(figure: plt.Figure, name: str) -> None:
    """Save a documentation figure with consistent dimensions and metadata."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        OUTPUT / name,
        dpi=150,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Regime Anomaly documentation figure generator"},
    )
    plt.close(figure)


def correlation_figure(frame: pd.DataFrame) -> None:
    columns = [
        "Usage_kWh",
        "Lagging_Current_Reactive.Power_kVarh",
        "Leading_Current_Reactive_Power_kVarh",
        "CO2(tCO2)",
        "Lagging_Current_Power_Factor",
        "Leading_Current_Power_Factor",
    ]
    labels = [
        "Usage",
        "Lagging reactive",
        "Leading reactive",
        "CO2",
        "Lagging PF",
        "Leading PF",
    ]
    correlation = frame[columns].corr(method="pearson")
    figure, axis = plt.subplots(figsize=(9.2, 7.1))
    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="vlag",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        xticklabels=labels,
        yticklabels=labels,
        cbar_kws={"label": "Pearson r"},
        ax=axis,
    )
    axis.set_title("Pearson correlation / Correlação de Pearson", weight="bold")
    axis.tick_params(axis="x", rotation=35)
    axis.tick_params(axis="y", rotation=0)
    save(figure, "correlation-matrix.png")


def month_hour_figure(frame: pd.DataFrame) -> None:
    dated = frame.assign(date=pd.to_datetime(frame["date"], dayfirst=True))
    profile = (
        dated.assign(month=dated["date"].dt.month, hour=dated["date"].dt.hour)
        .pivot_table(index="month", columns="hour", values="Usage_kWh", aggfunc="mean")
    )
    figure, axis = plt.subplots(figsize=(12.8, 5.8))
    sns.heatmap(
        profile,
        cmap="mako",
        cbar_kws={"label": "Mean consumption / Consumo médio (kWh)"},
        ax=axis,
    )
    axis.set_title("Mean consumption by month and hour / Consumo médio por mês e hora", weight="bold")
    axis.set_xlabel("Hour / Hora")
    axis.set_ylabel("Month / Mês")
    save(figure, "consumption-month-hour.png")


def kmeans_figure() -> None:
    output = notebook_output(NOTEBOOKS / "01_EDA.ipynb", 48)
    matches = re.findall(
        r"^\s*\d+\s+(\d+)\s+([0-9.]+)\s+([0-9.]+)",
        output,
        flags=re.MULTILINE,
    )
    if not matches:
        raise ValueError("K-Means diagnostics were not found in notebook 01 cell 48")
    diagnostics = pd.DataFrame(matches, columns=["k", "inertia", "silhouette"]).astype(float)

    figure, axes = plt.subplots(1, 2, figsize=(12.8, 4.6))
    axes[0].plot(diagnostics["k"], diagnostics["inertia"], marker="o", color=PALETTE["blue"])
    axes[0].set_title("Elbow diagnostic / Diagnóstico do cotovelo", weight="bold")
    axes[0].set_ylabel("Inertia / Inércia")
    axes[1].plot(
        diagnostics["k"],
        diagnostics["silhouette"],
        marker="o",
        color=PALETTE["orange"],
    )
    axes[1].set_title("Silhouette diagnostic / Diagnóstico de silhueta", weight="bold")
    axes[1].set_ylabel("Mean silhouette / Silhueta média")
    for axis in axes:
        axis.axvline(3, color=PALETTE["red"], linestyle="--", label="Problem hypothesis / Hipótese: K=3")
        axis.set_xlabel("Number of clusters / Número de clusters (K)")
        axis.grid(alpha=0.2)
        axis.legend()
    save(figure, "kmeans-diagnostics.png")


def preprocessing_figure() -> None:
    output = notebook_output(NOTEBOOKS / "02_preprocessing.ipynb", 13)
    matches = re.findall(
        r"Name:\s*(.*?)\s*\|\s*Silhouette:\s*([0-9.]+)\|\s*ARI:\s*([0-9.]+)",
        output,
    )
    if not matches:
        raise ValueError("Preprocessing diagnostics were not found in notebook 02 cell 13")
    diagnostics = pd.DataFrame(matches, columns=["configuration", "silhouette", "ari"])
    diagnostics[["silhouette", "ari"]] = diagnostics[["silhouette", "ari"]].astype(float)
    labels = ["Numeric", "+ hour", "+ month", "+ hour + month", "+ weekday", "+ weekday + PCA90"]
    if len(labels) != len(diagnostics):
        raise ValueError("Unexpected number of preprocessing configurations")

    figure, axis = plt.subplots(figsize=(12.8, 5.2))
    positions = range(len(diagnostics))
    width = 0.38
    axis.bar(
        [position - width / 2 for position in positions],
        diagnostics["silhouette"],
        width,
        label="Silhouette / Silhueta",
        color=PALETTE["blue"],
    )
    axis.bar(
        [position + width / 2 for position in positions],
        diagnostics["ari"],
        width,
        label="External ARI / ARI externo",
        color=PALETTE["orange"],
    )
    axis.set_xticks(list(positions), labels, rotation=18, ha="right")
    axis.set_ylim(0, 0.7)
    axis.set_ylabel("Score / Escore")
    axis.set_title("Stored preprocessing diagnostics / Diagnósticos armazenados do pré-processamento", weight="bold")
    axis.grid(axis="y", alpha=0.2)
    axis.legend()
    save(figure, "preprocessing-diagnostics.png")


def anomaly_tracking_figure() -> None:
    """Publish the post-hoc regime distribution of Isolation Forest signals."""
    source = ROOT / "artifacts" / "tables" / "tracking_anomalias_por_load_type.csv"
    if not source.exists():
        raise FileNotFoundError(f"Anomaly tracking table required for documentation: {source}")
    tracking = pd.read_csv(source)
    order = ["Light_Load", "Medium_Load", "Maximum_Load"]
    tracking["regime_referencia"] = pd.Categorical(
        tracking["regime_referencia"], categories=order, ordered=True
    )
    tracking = tracking.sort_values("regime_referencia")
    total_rate = tracking["Sinalizado"].sum() / tracking["total_registros"].sum()

    figure, axis = plt.subplots(figsize=(9.6, 4.8))
    sns.barplot(
        data=tracking,
        x="regime_referencia",
        y="taxa_sinalizada",
        color=PALETTE["red"],
        ax=axis,
    )
    axis.axhline(total_rate, color="#333333", linestyle="--", label="Overall rate / Taxa total")
    axis.set(
        title="Isolation Forest signal rate by reference regime / Taxa por regime",
        xlabel="Reference regime / Regime de referência",
        ylabel="Flagged proportion / Proporção sinalizada",
    )
    axis.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.1%}"))
    axis.grid(axis="y", alpha=0.2)
    axis.legend()
    save(figure, "isolation-forest-target-tracking.png")


def main() -> None:
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset required to generate documentation figures: {DATASET}")
    sns.set_theme(style="whitegrid", context="notebook")
    frame = pd.read_csv(DATASET, low_memory=False)
    correlation_figure(frame)
    month_hour_figure(frame)
    kmeans_figure()
    preprocessing_figure()
    anomaly_tracking_figure()


if __name__ == "__main__":
    main()
