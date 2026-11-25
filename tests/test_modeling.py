import dataclasses
import pickle

import joblib
import numpy as np
import pandas as pd
import pytest
from test_preprocessing import synthetic_raw

from regime_anomaly import modeling as md
from regime_anomaly import preprocessing as pp
from regime_anomaly.config import ARTIFACTS
from regime_anomaly.data import load_data


@pytest.fixture(scope="module")
def bundle_and_frame() -> tuple[md.ModelBundle, pd.DataFrame]:
    frame = pp.add_calendar_features(pp.parse_timestamps(synthetic_raw(days=4)))
    regime_pre = pp.build_feature_preprocessor("regime").fit(frame[pp.feature_columns("regime")])
    anomaly_pre = pp.build_feature_preprocessor("anomaly").fit(frame[pp.feature_columns("anomaly")])
    regime_input = regime_pre.transform(frame[pp.feature_columns("regime")])
    regime_model = md.make_regime_model("gmm_diag").fit(regime_input)
    anomaly_model = md.make_anomaly_model().fit(
        anomaly_pre.transform(frame[pp.feature_columns("anomaly")])
    )
    order = md.order_by_profile(regime_model.predict(regime_input), frame)
    bundle = md.ModelBundle(
        regime_feature_set="regime",
        regime_preprocessor=regime_pre,
        regime_model=regime_model,
        regime_order=order,
        regime_names=md.REGIME_NAMES,
        anomaly_feature_set="anomaly",
        anomaly_preprocessor=anomaly_pre,
        anomaly_model=anomaly_model,
        anomaly_threshold=0.0,
    )
    bundle.anomaly_threshold = float(np.quantile(bundle.anomaly_scores(frame), 0.99))
    return bundle, frame


def test_order_by_profile_names_regimes_by_electrical_signature() -> None:
    labels = np.array([5, 5, 9, 9, 1, 1])
    frame = pd.DataFrame(
        {
            pp.USAGE: [60, 50, 3.5, 4.0, 3.0, 3.2],
            pp.LEADING_KVARH: [0, 0, 17, 16, 0, 0],
        }
    )
    assert md.order_by_profile(labels, frame) == {1: 0, 9: 1, 5: 2}


def test_predict_outputs(bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame]) -> None:
    bundle, frame = bundle_and_frame
    result = bundle.predict(frame.drop(columns=pp.CALENDAR_FEATURES))
    assert set(result["regime"]) <= {0, 1, 2}
    assert result["regime_confidence"].between(0, 1).all()
    assert 0 < result["is_anomaly"].mean() <= 0.02
    medians = result.groupby("regime")[pp.USAGE].median()
    assert medians.idxmax() == 2
    assert set(result["regime_name"]) <= set(md.REGIME_NAMES)


def test_predict_ignores_label_values(
    bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame],
) -> None:
    bundle, frame = bundle_and_frame
    altered = frame.assign(load_type="Maximum_Load")
    pd.testing.assert_series_equal(
        bundle.predict(frame)["regime"], bundle.predict(altered)["regime"]
    )


UCI_NAMES = {
    "usage_kwh": "Usage_kWh",
    "lagging_current_reactive_power_kvarh": "Lagging_Current_Reactive.Power_kVarh",
    "leading_current_reactive_power_kvarh": "Leading_Current_Reactive_Power_kVarh",
    "lagging_current_power_factor": "Lagging_Current_Power_Factor",
    "leading_current_power_factor": "Leading_Current_Power_Factor",
    "nsm": "NSM",
    "weekstatus": "WeekStatus",
    "day_of_week": "Day_of_week",
}


def test_predict_accepts_original_uci_names(
    bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame],
) -> None:
    bundle, frame = bundle_and_frame
    original = frame.rename(columns=UCI_NAMES)
    assert pp.normalize_columns(original).columns.tolist() == frame.columns.tolist()
    pd.testing.assert_frame_equal(bundle.predict(original), bundle.predict(frame))


def test_predict_rejects_missing_columns(
    bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame],
) -> None:
    bundle, frame = bundle_and_frame
    with pytest.raises(ValueError, match="ausentes"):
        bundle.predict(frame.drop(columns=[pp.USAGE]))


def test_bundle_round_trips(bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame]) -> None:
    bundle, frame = bundle_and_frame
    restored = pickle.loads(pickle.dumps(bundle))
    pd.testing.assert_frame_equal(restored.predict(frame), bundle.predict(frame))


def test_regime_boundaries_in_row_order() -> None:
    regimes = np.array([0, 0, 2, 2, 2, 1])
    expected = np.array([False, True, True, False, True, True])
    assert (md.regime_boundaries(regimes) == expected).all()


def test_regime_boundaries_follow_time_not_row_order() -> None:
    times = pd.Series(pd.date_range("2018-01-01 00:15", periods=4, freq="15min"))
    shuffled = [2, 0, 3, 1]
    regimes = np.array([0, 0, 1, 1])[shuffled]
    boundary = md.regime_boundaries(regimes, times.iloc[shuffled].reset_index(drop=True))
    assert (boundary == np.array([False, True, True, False])[shuffled]).all()


def test_regime_boundaries_ignore_gaps() -> None:
    times = pd.Series(pd.to_datetime(["2018-01-01 00:15", "2018-01-01 00:30", "2018-01-01 05:00"]))
    assert not md.regime_boundaries(np.array([0, 0, 2]), times).any()


def test_transition_filter_only_removes_boundary_alerts(
    bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame],
) -> None:
    bundle, frame = bundle_and_frame
    unfiltered = bundle.predict(frame)
    assert (unfiltered["is_anomaly"] == unfiltered["is_anomaly_raw"]).all()

    filtered_bundle = md.ModelBundle(**{**bundle.__dict__, "transition_filter": True})
    filtered = filtered_bundle.predict(frame)
    assert not (filtered["is_anomaly"] & filtered["regime_boundary"]).any()
    expected = filtered["is_anomaly_raw"] & ~filtered["regime_boundary"]
    assert (filtered["is_anomaly"] == expected).all()


def test_bundles_pickled_without_filter_field_default_to_off(
    bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame],
) -> None:
    bundle, frame = bundle_and_frame
    legacy = pickle.loads(pickle.dumps(bundle))
    del legacy.__dict__["transition_filter"]
    assert legacy.transition_filter is False
    assert (legacy.predict(frame)["is_anomaly"] == legacy.predict(frame)["is_anomaly_raw"]).all()


def test_kmeans_bundle_has_no_confidence_column(
    bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame],
) -> None:
    """The published model is K-Means, which has no ``predict_proba``."""
    bundle, frame = bundle_and_frame
    regime_input = bundle.regime_preprocessor.transform(frame[pp.feature_columns("regime")])
    kmeans = md.make_regime_model("kmeans").fit(regime_input)
    order = md.order_by_profile(kmeans.predict(regime_input), frame)
    result = dataclasses.replace(bundle, regime_model=kmeans, regime_order=order).predict(frame)
    assert "regime_confidence" not in result
    assert set(result["regime_name"]) <= set(md.REGIME_NAMES)


def test_predict_rejects_unknown_week_status(
    bundle_and_frame: tuple[md.ModelBundle, pd.DataFrame],
) -> None:
    bundle, frame = bundle_and_frame
    with pytest.raises(ValueError, match="WeekStatus"):
        bundle.predict(frame.assign(weekstatus="weekend"))


PUBLISHED_MODEL = ARTIFACTS / "models" / "final_model.joblib"


@pytest.mark.skipif(not PUBLISHED_MODEL.exists(), reason="modelo publicado ausente")
def test_published_model_scores_raw_uci_rows() -> None:
    raw = load_data().head(200)
    result = joblib.load(PUBLISHED_MODEL).predict(raw)
    assert len(result) == len(raw)
    assert set(result["regime_name"]) <= set(md.REGIME_NAMES)
    assert {"anomaly_score", "is_anomaly_raw", "regime_boundary", "is_anomaly"} <= set(result)
