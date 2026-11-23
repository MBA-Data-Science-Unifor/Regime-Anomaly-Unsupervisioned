"""Read-only helpers for the Streamlit monitoring dashboard."""

from __future__ import annotations

import json

import pandas as pd

from .config import ARTIFACTS

RESULTS_PATH = ARTIFACTS / "data" / "processed" / "analysis_results.csv"
METRICS_PATH = ARTIFACTS / "metadata" / "final_metrics.json"

# Accept original UCI names during the transition; publish canonical names later.
COLUMN_ALIASES = {
    "date": "timestamp",
    "Usage_kWh": "energy_consumption_kwh",
    "Lagging_Current_Reactive.Power_kVarh": "lagging_reactive_energy_kvarh",
    "Leading_Current_Reactive_Power_kVarh": "leading_reactive_energy_kvarh",
    "Lagging_Current_Power_Factor": "lagging_power_factor_pct",
    "Leading_Current_Power_Factor": "leading_power_factor_pct",
    "CO2(tCO2)": "co2_emissions_tco2",
    "NSM": "seconds_since_midnight",
    "WeekStatus": "day_type",
    "Day_of_week": "day_of_week",
    "Load_Type": "reference_load_type",
}

DISPLAY_COLUMNS = {
    "energy_consumption_kwh": "Consumo de energia (kWh)",
    "lagging_reactive_energy_kvarh": "Energia reativa atrasada (kvarh)",
    "leading_reactive_energy_kvarh": "Energia reativa adiantada (kvarh)",
    "lagging_power_factor_pct": "Fator de potência atrasado (%)",
    "leading_power_factor_pct": "Fator de potência adiantado (%)",
    "co2_emissions_tco2": "Emissões de CO₂",
    "anomaly_score": "Índice de atipicidade",
}


def artifact_status() -> dict[str, bool]:
    """Return availability of optional dashboard artifacts."""
    return {
        "results": RESULTS_PATH.exists(),
        "metrics": METRICS_PATH.exists(),
        "model": (ARTIFACTS / "models" / "final_model.joblib").exists(),
        "preprocessor": (ARTIFACTS / "models" / "preprocessor.joblib").exists(),
    }


def results_version() -> int:
    """Use file mtime as a cache key without writing any artifact."""
    return RESULTS_PATH.stat().st_mtime_ns if RESULTS_PATH.exists() else 0


def load_results(_version: int) -> pd.DataFrame:
    """Load and normalize published monitoring results, if available."""
    if not RESULTS_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(RESULTS_PATH)
    frame = frame.rename(
        columns={key: value for key, value in COLUMN_ALIASES.items() if key in frame}
    )
    if "timestamp" in frame:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", dayfirst=True)
        frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")
    if "seconds_since_midnight" in frame and "hour_of_day" not in frame:
        frame["hour_of_day"] = (
            pd.to_numeric(frame["seconds_since_midnight"], errors="coerce") // 3600
        )
    return frame


def load_metrics() -> dict[str, object]:
    """Load final metrics only when explicitly published."""
    return json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {}


def available_measurements(frame: pd.DataFrame) -> list[str]:
    """Return supported numeric telemetry in a stable dashboard order."""
    return [
        name
        for name in DISPLAY_COLUMNS
        if name in frame and pd.api.types.is_numeric_dtype(frame[name])
    ]


def alert_severity(frame: pd.DataFrame) -> pd.Series:
    """Provide conservative display severity until the pipeline publishes one."""
    if "alert_severity" in frame:
        return frame["alert_severity"].fillna("Normal").astype(str)
    if "is_anomaly" in frame:
        return frame["is_anomaly"].map({True: "Atenção", False: "Normal"}).fillna("Normal")
    return pd.Series("Sem classificação", index=frame.index)
