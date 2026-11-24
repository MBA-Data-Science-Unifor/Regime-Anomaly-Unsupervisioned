import pickle

import numpy as np
import pandas as pd
import pytest

from regime_anomaly import preprocessing as pp
from regime_anomaly.data import LABEL_COLUMN


def synthetic_raw(days: int = 3) -> pd.DataFrame:
    """Mimic the source layout, including the day-closing 00:00 row stored last."""
    rows = []
    start = pd.Timestamp("2018-08-30")
    rng = np.random.default_rng(0)
    for offset in range(days):
        day = start + pd.Timedelta(days=offset)
        for nsm in [*range(900, 86_400, 900), 0]:
            stamp = day + pd.Timedelta(seconds=nsm)
            usage = float(rng.uniform(0, 100))
            rows.append(
                {
                    "date": stamp.strftime("%d/%m/%Y %H:%M"),
                    pp.USAGE: usage,
                    pp.LAGGING_KVARH: float(rng.uniform(0, 50)),
                    pp.LEADING_KVARH: float(rng.uniform(0, 20)),
                    pp.CO2: round(usage * 0.0005, 2),
                    pp.LAGGING_PF: float(rng.uniform(40, 100)),
                    pp.LEADING_PF: float(rng.uniform(40, 100)),
                    pp.NSM: nsm,
                    pp.WEEK_STATUS: "Weekend" if day.day_of_week >= 5 else "Weekday",
                    pp.DAY_OF_WEEK: day.day_name(),
                    LABEL_COLUMN: "Light_Load",
                }
            )
    return pd.DataFrame(rows)


def test_day_closing_reading_moves_to_next_midnight() -> None:
    prepared = pp.parse_timestamps(synthetic_raw())
    assert prepared[pp.TIMESTAMP_COLUMN].is_monotonic_increasing
    assert prepared[pp.TIMESTAMP_COLUMN].diff().dropna().eq(pp.EXPECTED_FREQUENCY).all()
    closing = prepared.loc[prepared[pp.NSM] == 0, pp.TIMESTAMP_COLUMN].iloc[0]
    assert closing == pd.Timestamp("2018-08-31 00:00")


def test_validation_rejects_gaps() -> None:
    prepared = pp.parse_timestamps(synthetic_raw()).drop(index=10)
    with pytest.raises(ValueError, match="intervalos_irregulares"):
        pp.validate_frame(prepared)


def test_calendar_features_are_bounded() -> None:
    prepared = pp.add_calendar_features(pp.parse_timestamps(synthetic_raw()))
    trig = prepared[["hour_sin", "hour_cos", "dow_sin", "dow_cos"]]
    assert trig.abs().le(1).all().all()
    assert np.allclose(prepared["hour_sin"] ** 2 + prepared["hour_cos"] ** 2, 1)
    assert set(prepared["is_weekend"]) <= {0.0, 1.0}


def test_split_is_chronological_and_boundary_reading_stays_earlier() -> None:
    boundaries = (pd.Timestamp("2018-08-31"), pd.Timestamp("2018-09-01"))
    prepared, _ = pp.prepare_frame(synthetic_raw(), boundaries)
    by_split = prepared.groupby(pp.SPLIT_COLUMN)[pp.TIMESTAMP_COLUMN]
    assert by_split.max()["train"] == boundaries[0]
    assert by_split.min()["validation"] > boundaries[0]
    assert by_split.max()["train"] < by_split.min()["validation"]
    assert by_split.max()["validation"] < by_split.min()["test"]


@pytest.mark.parametrize("feature_set", sorted(pp.FEATURE_SETS))
def test_preprocessor_fits_on_train_and_never_uses_label(feature_set: str) -> None:
    prepared, _ = pp.prepare_frame(
        synthetic_raw(), (pd.Timestamp("2018-08-31"), pd.Timestamp("2018-09-01"))
    )
    columns = pp.feature_columns(feature_set)
    assert LABEL_COLUMN not in columns
    assert pp.CO2 not in columns

    train = prepared[prepared[pp.SPLIT_COLUMN] == "train"]
    test = prepared[prepared[pp.SPLIT_COLUMN] == "test"]
    preprocessor = pp.build_preprocessor(feature_set).fit(train[columns])

    transformed_train = preprocessor.transform(train[columns])
    assert transformed_train.shape == (len(train), len(columns))
    assert np.allclose(transformed_train.mean(axis=0), 0, atol=1e-9)
    assert np.isfinite(preprocessor.transform(test[columns])).all()
    pickle.loads(pickle.dumps(preprocessor))


def test_regime_set_excludes_calendar() -> None:
    assert not set(pp.feature_columns("regime")) & set(pp.CALENDAR_FEATURES)


def test_label_guard() -> None:
    with pytest.raises(ValueError):
        pp.assert_no_label([pp.USAGE, LABEL_COLUMN])
