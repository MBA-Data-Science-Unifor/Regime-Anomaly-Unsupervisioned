import numpy as np
import pandas as pd
from test_preprocessing import synthetic_raw

from regime_anomaly import preprocessing as pp
from regime_anomaly.experiments import (
    cluster_label_agreement,
    supervised_comparison,
    unsupervised_sensitivity,
)


def experiment_splits() -> dict[str, pd.DataFrame]:
    prepared, _ = pp.prepare_frame(
        synthetic_raw(), (pd.Timestamp("2018-08-31"), pd.Timestamp("2018-09-01"))
    )
    prepared[pp.LABEL] = np.resize(["Light_Load", "Medium_Load", "Maximum_Load"], len(prepared))
    return {
        name: prepared[prepared[pp.SPLIT_COLUMN] == name].reset_index(drop=True)
        for name in pp.SPLIT_NAMES
    }


def test_selection_does_not_depend_on_test_labels() -> None:
    splits = experiment_splits()
    first, _, _, _ = supervised_comparison(splits)
    altered = dict(splits)
    altered["test"] = splits["test"].assign(
        **{pp.LABEL: splits["test"][pp.LABEL].iloc[::-1].to_numpy()}
    )
    second, _, _, _ = supervised_comparison(altered)
    pd.testing.assert_frame_equal(first, second)


def test_unsupervised_sensitivity_is_independent_of_labels() -> None:
    splits = experiment_splits()
    altered = {name: frame.drop(columns=pp.LABEL) for name, frame in splits.items()}
    regimes, anomalies = unsupervised_sensitivity(altered)
    assert set(regimes.index) == {"cinco_variaveis", "sem_fp_adiantado"}
    assert set(anomalies.index) == {256, 1024}
    assert anomalies["jaccard_sementes_medio"].between(0, 1).all()


def test_cluster_agreement_uses_train_mapping_and_arbitrary_cluster_ids() -> None:
    class FixedClusters:
        def predict(self, features):
            return features[:, 0].astype(int)

    splits = {
        "train": pd.DataFrame({pp.LABEL: ["A", "A", "B", "B"]}),
        "validation": pd.DataFrame({pp.LABEL: ["B", "A"]}),
        "test": pd.DataFrame({pp.LABEL: ["B", "A"]}),
    }
    data = {
        "regime": {
            "train": np.array([[7], [7], [3], [3]]),
            "validation": np.array([[7], [3]]),
            "test": np.array([[7], [3]]),
        }
    }
    result = cluster_label_agreement({("regime", "fixed"): FixedClusters()}, data, splits)
    assert result.loc[("regime", "fixed", "test"), "acuracia"] == 0.0
    assert result.loc[("regime", "fixed", "test"), "ari"] == 1.0
