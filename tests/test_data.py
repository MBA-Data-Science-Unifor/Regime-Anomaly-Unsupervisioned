from pathlib import Path

import pandas as pd
import pytest

from regime_anomaly import LABEL_COLUMN, load_data


def test_load_data_preserves_original_column_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_columns = [
        "date",
        "Usage_kWh",
        "CO2(tCO2)",
        "Day_of_week",
        "Load_Type",
    ]
    original_frame = pd.DataFrame(
        [["01/01/2018 00:15", 3.17, 0, "Monday", "Light_Load"]],
        columns=expected_columns,
    )
    monkeypatch.setattr(
        "regime_anomaly.data.pd.read_csv",
        lambda *_args, **_kwargs: original_frame.copy(),
    )

    frame = load_data(Path(__file__))

    assert frame.columns.tolist() == expected_columns
    assert LABEL_COLUMN == "Load_Type"
