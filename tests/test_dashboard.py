import pandas as pd

from regime_anomaly.dashboard import parse_timestamps


def test_parse_timestamps_keeps_iso_days_above_twelve_and_uci_dates() -> None:
    values = pd.Series(["2018-01-13 00:15:00", "2019-01-01 00:00:00", "13/01/2018 00:30"])
    parsed = parse_timestamps(values)
    assert parsed.tolist() == [
        pd.Timestamp("2018-01-13 00:15"),
        pd.Timestamp("2019-01-01 00:00"),
        pd.Timestamp("2018-01-13 00:30"),
    ]
