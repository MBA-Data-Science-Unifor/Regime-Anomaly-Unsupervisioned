"""Retrospective, non-publishing comparisons for the modeling notebooks."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, IsolationForest
from sklearn.metrics import (
    accuracy_score,
    adjusted_rand_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    normalized_mutual_info_score,
    silhouette_score,
)
from sklearn.neighbors import KNeighborsClassifier

from . import preprocessing as pp


def cluster_label_agreement(
    reference_models: dict, transformed: dict, splits: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """Assess fitted clusters against labels with a mapping learned from train only.

    This is post-hoc agreement, not supervised model training or model selection.
    Several clusters may map to the same class; ARI/NMI do not require mapping.
    """
    rows = []
    train_labels = splits["train"][pp.LABEL].to_numpy()
    majority = pd.Series(train_labels).value_counts().idxmax()
    for (feature_set, candidate), model in reference_models.items():
        clusters_train = model.predict(transformed[feature_set]["train"])
        counts = pd.crosstab(clusters_train, train_labels)
        mapping = counts.idxmax(axis=1).to_dict()
        for part in ("validation", "test"):
            clusters = model.predict(transformed[feature_set][part])
            truth = splits[part][pp.LABEL].to_numpy()
            predicted = np.array([mapping.get(cluster, majority) for cluster in clusters])
            rows.append(
                {
                    "conjunto": feature_set,
                    "candidato": candidate,
                    "particao": part,
                    "ari": adjusted_rand_score(truth, clusters),
                    "nmi": normalized_mutual_info_score(truth, clusters),
                    "acuracia": accuracy_score(truth, predicted),
                    "acuracia_balanceada": balanced_accuracy_score(truth, predicted),
                    "f1_macro": f1_score(truth, predicted, average="macro", zero_division=0),
                }
            )
    return pd.DataFrame(rows).set_index(["conjunto", "candidato", "particao"])


def supervised_comparison(splits: dict[str, pd.DataFrame], *, alternatives: bool = False):
    """Fit on train, select on validation and report retrospective test metrics.

    No fitted model or result is published; return data frames for notebook display.
    """
    train, validation, test = (splits[name] for name in pp.SPLIT_NAMES)
    fitted, rows = {}, []
    for feature_set in ("regime", "regime_with_calendar"):
        columns = pp.feature_columns(feature_set)
        transformer = pp.build_feature_preprocessor(feature_set).fit(train[columns])
        x_train, x_val, x_test = (
            transformer.transform(frame[columns]) for frame in (train, validation, test)
        )
        candidates = {
            f"knn_{k}": KNeighborsClassifier(n_neighbors=k, n_jobs=1) for k in (5, 15, 31)
        }
        if alternatives:
            candidates.update(
                {
                    "knn_31_distance": KNeighborsClassifier(
                        n_neighbors=31, weights="distance", n_jobs=1
                    ),
                    "extra_trees": ExtraTreesClassifier(
                        n_estimators=150, min_samples_leaf=5, random_state=42, n_jobs=1
                    ),
                }
            )
        for name, model in candidates.items():
            model.fit(x_train, train[pp.LABEL])
            prediction = model.predict(x_val)
            fitted[(feature_set, name)] = (model, x_test)
            rows.append(
                {
                    "features": feature_set,
                    "modelo": name,
                    "f1_macro_validacao": f1_score(
                        validation[pp.LABEL], prediction, average="macro", zero_division=0
                    ),
                    "acuracia_balanceada_validacao": balanced_accuracy_score(
                        validation[pp.LABEL], prediction
                    ),
                }
            )
    comparison = (
        pd.DataFrame(rows)
        .sort_values(["f1_macro_validacao", "features", "modelo"], ascending=[False, True, True])
        .reset_index(drop=True)
    )
    best = comparison.iloc[0]
    model, x_test = fitted[(best["features"], best["modelo"])]
    prediction = model.predict(x_test)
    baseline = (
        DummyClassifier(strategy="most_frequent")
        .fit(np.zeros((len(train), 1)), train[pp.LABEL])
        .predict(np.zeros((len(test), 1)))
    )
    y_test = test[pp.LABEL]
    summary = pd.DataFrame(
        [
            {
                "modelo": name,
                "acuracia": accuracy_score(y_test, pred),
                "acuracia_balanceada": balanced_accuracy_score(y_test, pred),
                "f1_macro": f1_score(y_test, pred, average="macro", zero_division=0),
            }
            for name, pred in (("selecionado", prediction), ("classe_majoritaria", baseline))
        ]
    ).set_index("modelo")
    report = pd.DataFrame(
        classification_report(y_test, prediction, output_dict=True, zero_division=0)
    ).T
    confusion = pd.crosstab(
        pd.Series(y_test, name="observado"), pd.Series(prediction, name="previsto")
    )
    return comparison, summary, report, confusion


def unsupervised_sensitivity(splits: dict[str, pd.DataFrame]):
    """Compare clustering and anomaly stability on validation, without fault claims."""
    train, validation = (splits[name] for name in ("train", "validation"))
    columns = pp.feature_columns("regime")
    transformer = pp.build_feature_preprocessor("regime").fit(train[columns])
    x_train = transformer.transform(train[columns])
    x_val = transformer.transform(validation[columns])
    # The transformed numeric columns preserve feature_columns order.
    drop = columns.index(pp.LEADING_PF)
    regimes = []
    for name, xt, xv in (
        ("cinco_variaveis", x_train, x_val),
        ("sem_fp_adiantado", np.delete(x_train, drop, axis=1), np.delete(x_val, drop, axis=1)),
    ):
        models = [
            KMeans(n_clusters=3, n_init=20, random_state=seed).fit(xt) for seed in (42, 43, 44)
        ]
        labels = [model.predict(xv) for model in models]
        regimes.append(
            {
                "configuracao": name,
                "silhueta": silhouette_score(
                    xv, labels[0], sample_size=min(3000, len(xv)), random_state=42
                ),
                "menor_grupo": np.bincount(labels[0], minlength=3).min() / len(xv),
                "ari_sementes_medio": np.mean(
                    [adjusted_rand_score(labels[0], lab) for lab in labels[1:]]
                ),
            }
        )
    columns = pp.feature_columns("anomaly")
    anomaly_pre = pp.build_feature_preprocessor("anomaly").fit(train[columns])
    xt, xv = (anomaly_pre.transform(frame[columns]) for frame in (train, validation))
    anomaly_rows = []
    for max_samples in (256, 1024):
        scores = [
            -IsolationForest(
                n_estimators=150, max_samples=min(max_samples, len(xt)), random_state=seed, n_jobs=1
            )
            .fit(xt)
            .score_samples(xv)
            for seed in (42, 43, 44)
        ]
        flags = [s >= np.quantile(s, 0.99) for s in scores]
        jaccard = [
            np.logical_and(flags[0], f).sum() / np.logical_or(flags[0], f).sum() for f in flags[1:]
        ]
        anomaly_rows.append(
            {
                "max_samples": max_samples,
                "taxa_validacao": flags[0].mean(),
                "jaccard_sementes_medio": np.mean(jaccard),
            }
        )
    return pd.DataFrame(regimes).set_index("configuracao"), pd.DataFrame(anomaly_rows).set_index(
        "max_samples"
    )
