"""Read-only helpers for the Streamlit monitoring dashboard."""

from __future__ import annotations

import hashlib
import json

import pandas as pd

from .config import ARTIFACTS

RESULTS_PATH = ARTIFACTS / "data" / "processed" / "analysis_results.csv"
METRICS_PATH = ARTIFACTS / "metadata" / "final_metrics.json"
MODEL_PATH = ARTIFACTS / "models" / "final_model.joblib"
PREPROCESSING_PATH = ARTIFACTS / "metadata" / "preprocessing.json"
PREPARED_PATH = ARTIFACTS / "data" / "processed" / "prepared_dataset.csv"
MANIFEST_PATH = ARTIFACTS / "metadata" / "manifest.json"
RAW_PATH = ARTIFACTS / "data" / "raw" / "Steel_industry_data.csv"


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
    # snake_case names published by notebooks 03-05 (analysis_results.csv)
    "usage_kwh": "energy_consumption_kwh",
    "lagging_current_reactive_power_kvarh": "lagging_reactive_energy_kvarh",
    "leading_current_reactive_power_kvarh": "leading_reactive_energy_kvarh",
    "lagging_current_power_factor": "lagging_power_factor_pct",
    "leading_current_power_factor": "leading_power_factor_pct",
    "co2_tco2": "co2_emissions_tco2",
    "nsm": "seconds_since_midnight",
    "weekstatus": "day_type",
    "load_type": "reference_load_type",
    "regime_name": "cluster_operational_profile",
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
        "preprocessing": PREPROCESSING_PATH.exists(),
        "prepared": PREPARED_PATH.exists(),
    }


def metrics_version() -> int:
    """Cache key for ``final_metrics.json`` (its own mtime, not the results file's)."""
    return METRICS_PATH.stat().st_mtime_ns if METRICS_PATH.exists() else 0


def results_version() -> int:
    """Use file mtime as a cache key without writing any artifact."""
    return RESULTS_PATH.stat().st_mtime_ns if RESULTS_PATH.exists() else 0


def artifact_versions() -> tuple[int, ...]:
    """Version watched artifacts so changes trigger a dashboard refresh."""
    return tuple(
        path.stat().st_mtime_ns if path.exists() else 0
        for path in (
            RESULTS_PATH,
            METRICS_PATH,
            MODEL_PATH,
            PREPROCESSING_PATH,
            PREPARED_PATH,
            MANIFEST_PATH,
            RAW_PATH,
        )
    )


def audit_artifacts() -> pd.DataFrame:
    """Compare notebook outputs and raw data against the published manifest."""
    entries = [
        ("Dados brutos", RAW_PATH, "Fonte UCI"),
        ("Base preparada", PREPARED_PATH, "Notebook 02"),
        ("Preparação", PREPROCESSING_PATH, "Notebook 02"),
        ("Resultados", RESULTS_PATH, "Notebook 03"),
        ("Métricas", METRICS_PATH, "Notebook 03"),
        ("Modelo", MODEL_PATH, "Notebook 03"),
    ]
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            manifest = {}
    except (OSError, ValueError):
        manifest = {}
    rows = []
    for name, path, origin in entries:
        key = path.relative_to(ARTIFACTS).as_posix()
        expected = (
            manifest.get("dados_brutos", {}).get("sha256")
            if path == RAW_PATH
            else manifest.get("artefatos", {}).get(key)
        )
        if not path.is_file():
            status = "Ausente"
        elif not expected:
            status = "Não verificado"
        else:
            try:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                status = "Íntegro" if digest == expected else "Divergente"
            except OSError:
                status = "Indisponível"
        rows.append({"Artefato": name, "Origem": origin, "Arquivo": key, "Integridade": status})
    audit = pd.DataFrame(rows)
    # Metadata must describe the same raw file; equal file hashes alone do not
    # guarantee that outputs from different runs share the same provenance.
    try:
        prep = json.loads(PREPROCESSING_PATH.read_text(encoding="utf-8"))
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        source_hashes = [
            prep.get("fonte", {}).get("sha256"),
            metrics.get("dados_sha256"),
            manifest.get("dados_brutos", {}).get("sha256"),
        ]
        known = {value for value in source_hashes if value}
        if len(known) > 1:
            affected = audit["Artefato"].isin(
                ["Base preparada", "Preparação", "Resultados", "Métricas", "Modelo"]
            )
            audit.loc[affected & (audit["Integridade"] == "Íntegro"), "Integridade"] = (
                "Proveniência divergente"
            )
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return audit


def parse_timestamps(values: pd.Series) -> pd.Series:
    """Parse ISO timestamps (published results) and UCI ``dd/mm/yyyy HH:MM`` dates.

    ``dayfirst=True`` alone misreads ISO strings whose day is above 12 and turns them
    into NaT, so ISO is tried first and day-first only fills what is left.
    """
    parsed = pd.to_datetime(values, format="ISO8601", errors="coerce")
    missing = parsed.isna()
    if missing.any():
        parsed[missing] = pd.to_datetime(values[missing], dayfirst=True, errors="coerce")
    return parsed


def load_results(_version: int) -> pd.DataFrame:
    """Load and normalize published monitoring results, if available."""
    if not RESULTS_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(RESULTS_PATH)
    frame = frame.rename(
        columns={key: value for key, value in COLUMN_ALIASES.items() if key in frame}
    )
    for column in ("is_anomaly", "is_anomaly_raw", "regime_boundary"):
        if column in frame:
            frame[column] = (
                frame[column]
                .map(
                    {
                        True: True,
                        False: False,
                        "True": True,
                        "False": False,
                        "true": True,
                        "false": False,
                    }
                )
                .astype("boolean")
            )
    if "timestamp" in frame:
        frame["timestamp"] = parse_timestamps(frame["timestamp"])
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
        return (
            frame["is_anomaly"].map({True: "Atenção", False: "Normal"}).fillna("Sem classificação")
        )
    return pd.Series("Sem classificação", index=frame.index)


def alert_masks(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Return kept and suppressed flags without inventing missing raw labels."""
    empty = pd.Series(False, index=frame.index)
    kept = frame["is_anomaly"].fillna(False).astype(bool) if "is_anomaly" in frame else empty
    if "is_anomaly_raw" not in frame or "is_anomaly" not in frame:
        return kept, empty.copy()
    raw = frame["is_anomaly_raw"].eq(True).fillna(False)
    known_unfiltered = frame["is_anomaly"].eq(False).fillna(False)
    return kept, raw & known_unfiltered


def daily_alert_counts(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the two published alert states on calendar days of the timestamps."""
    kept, suppressed = alert_masks(frame)
    values = pd.DataFrame(
        {"timestamp": frame["timestamp"], "Mantidos": kept, "Suprimidos": suppressed}
    )
    return values.set_index("timestamp").resample("D").sum().reset_index()


def load_preprocessing_data():
    if not PREPROCESSING_PATH.exists():
        return {}
    return json.loads(PREPROCESSING_PATH.read_text(encoding="utf-8"))
