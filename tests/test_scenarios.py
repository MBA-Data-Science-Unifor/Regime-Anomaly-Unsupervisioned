import numpy as np
import pandas as pd
import pytest

from regime_anomaly import preprocessing as pp
from regime_anomaly.scenarios import anomaly_scenarios


class FakeBundle:
    def predict(self, frame):
        result = frame.copy()
        result["anomaly_score"] = result[pp.USAGE] / 100
        result["is_anomaly_raw"] = result["anomaly_score"] >= 1
        result["regime_boundary"] = result["is_anomaly_raw"]
        result["is_anomaly"] = result["is_anomaly_raw"] & ~result["regime_boundary"]
        result["regime_name"] = "perfil"
        return result


def test_scenarios_keep_input_and_show_raw_and_filtered_decisions() -> None:
    frame = pd.DataFrame(
        {
            pp.TIMESTAMP_COLUMN: pd.date_range("2018-09-01 00:15", periods=96, freq="15min"),
            pp.SPLIT_COLUMN: "validation",
            pp.USAGE: np.full(96, 10.0),
            pp.LEADING_KVARH: np.full(96, 2.0),
            pp.LAGGING_PF: np.full(96, 90.0),
        }
    )
    before = frame.copy(deep=True)
    result = anomaly_scenarios(FakeBundle(), frame).set_index("cenario")
    pd.testing.assert_frame_equal(frame, before)
    assert not result.loc["Referência histórica", "alerta_bruto"]
    assert result.loc["Consumo elevado", "alerta_bruto"]
    assert result.loc["Consumo elevado", "fronteira"]
    assert not result.loc["Consumo elevado", "alerta_filtrado"]
    assert result["timestamp"].nunique() == 1


def test_scenarios_require_validation_readings() -> None:
    with pytest.raises(ValueError, match="validação"):
        anomaly_scenarios(FakeBundle(), pd.DataFrame({pp.SPLIT_COLUMN: ["train"]}))


def test_scenarios_support_custom_inputs_and_reject_invalid_values() -> None:
    frame = pd.DataFrame(
        {
            pp.TIMESTAMP_COLUMN: pd.date_range("2018-09-01 00:15", periods=96, freq="15min"),
            pp.SPLIT_COLUMN: "validation",
            pp.USAGE: 10.0,
            pp.LEADING_KVARH: 2.0,
            pp.LAGGING_PF: 90.0,
        }
    )
    result = anomaly_scenarios(FakeBundle(), frame, day="2018-09-01", custom={pp.USAGE: 200})
    assert result.set_index("cenario").loc["Cenário personalizado", "consumo_kwh"] == 200
    with pytest.raises(ValueError, match="inválidos"):
        anomaly_scenarios(FakeBundle(), frame, custom={pp.LAGGING_PF: 101})
