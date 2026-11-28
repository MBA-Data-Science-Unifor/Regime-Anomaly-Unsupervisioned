"""Controlled, non-publishing sensitivity scenarios for the anomaly detector."""

from __future__ import annotations

import pandas as pd

from . import preprocessing as pp


def anomaly_scenarios(bundle, prepared: pd.DataFrame, *, day=None, custom=None) -> pd.DataFrame:
    """Perturb one validation reading in its original day and keep neighbors intact.

    These artificial inputs are sensitivity probes, not verified fault examples.
    The raw and filtered decisions are both returned because the transition filter
    uses adjacent readings. Neither the supplied frame nor the model is modified.
    """
    validation = prepared.loc[prepared[pp.SPLIT_COLUMN] == "validation"].copy()
    if validation.empty:
        raise ValueError("Não há leituras de validação para criar cenários.")
    validation[pp.TIMESTAMP_COLUMN] = pd.to_datetime(validation[pp.TIMESTAMP_COLUMN])
    validation = validation.sort_values(pp.TIMESTAMP_COLUMN).reset_index(drop=True)
    interval_days = (validation[pp.TIMESTAMP_COLUMN] - pp.EXPECTED_FREQUENCY).dt.normalize()
    first_day = pd.Timestamp(day).normalize() if day is not None else interval_days.iloc[0]
    day = validation.loc[interval_days == first_day].reset_index(drop=True)
    if len(day) < 3 or not day[pp.TIMESTAMP_COLUMN].diff().dropna().eq(pp.EXPECTED_FREQUENCY).all():
        raise ValueError("São necessárias pelo menos três leituras consecutivas no dia.")
    original = bundle.predict(day)
    candidates = original.loc[~original["regime_boundary"] & ~original["is_anomaly_raw"]].copy()
    candidates = candidates.loc[(candidates.index > 0) & (candidates.index < len(day) - 1)]
    if candidates.empty:
        raise ValueError("Não há leitura de referência sem alerta e fora de fronteira nesse dia.")
    idx = (candidates["anomaly_score"] - candidates["anomaly_score"].median()).abs().idxmin()
    baseline = day.loc[idx]
    changes = [
        ("Referência histórica", {}),
        ("Consumo elevado", {pp.USAGE: max(float(baseline[pp.USAGE]) * 3, 150.0)}),
        ("Reativa adiantada elevada", {pp.LEADING_KVARH: 50.0}),
        ("Fator de potência atrasado baixo", {pp.LAGGING_PF: 5.0}),
        (
            "Consumo e reativa elevados",
            {pp.USAGE: max(float(baseline[pp.USAGE]) * 3, 150.0), pp.LEADING_KVARH: 50.0},
        ),
        (
            "Estresse combinado intenso",
            {pp.USAGE: 500.0, pp.LEADING_KVARH: 100.0, pp.LAGGING_PF: 1.0},
        ),
    ]
    if custom is not None:
        permitted = {pp.USAGE, pp.LEADING_KVARH, pp.LAGGING_PF}
        if set(custom) - permitted:
            raise ValueError("O cenário personalizado contém variáveis não suportadas.")
        for column, value in custom.items():
            if pd.isna(value) or value < 0 or (column == pp.LAGGING_PF and value > 100):
                raise ValueError(
                    "Valores de cenário inválidos: energia deve ser não negativa e FP entre 0 e 100."
                )
        changes.append(("Cenário personalizado", custom))
    records = []
    reference_score = float(original.loc[idx, "anomaly_score"])
    for name, modifications in changes:
        scenario = day.copy(deep=True)
        for column, value in modifications.items():
            scenario.loc[idx, column] = value
        result = bundle.predict(scenario).loc[idx]
        records.append(
            {
                "cenario": name,
                "timestamp": scenario.loc[idx, pp.TIMESTAMP_COLUMN],
                "consumo_kwh": scenario.loc[idx, pp.USAGE],
                "reativa_adiantada_kvarh": scenario.loc[idx, pp.LEADING_KVARH],
                "fp_atrasado_pct": scenario.loc[idx, pp.LAGGING_PF],
                "regime": result["regime_name"],
                "escore": result["anomaly_score"],
                "diferenca_escore": result["anomaly_score"] - reference_score,
                "alerta_bruto": bool(result["is_anomaly_raw"]),
                "fronteira": bool(result["regime_boundary"]),
                "alerta_filtrado": bool(result["is_anomaly"]),
            }
        )
    return pd.DataFrame(records)
