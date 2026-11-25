# Modeling

Modeling is implemented in `artifacts/notebooks/03_Modeling.ipynb`; the code that must
match between the notebook and inference lives in `src/regime_anomaly/modeling.py`.

## Protocol (fixed before results)

- **Data:** train January–August, validation September–October, test November–December.
  Every fit uses train only.
- **Regime candidates (three groups):** K-Means (`n_init=20`), GMM with diagonal
  covariance and GMM with full covariance (`n_init=5`), each on the `regime` feature set
  (primary) and on `regime_with_calendar` (sensitivity).
- **Evidence on validation:** silhouette, Davies–Bouldin, Calinski–Harabasz, smallest
  group share, seed stability (5 seeds), stability across 10 bootstraps by day, and
  temporal stability (agreement with a model refitted on validation).
- **Selection rule:** among `regime` candidates, eligible if mean bootstrap ARI ≥ 0.80
  and smallest group ≥ 5%; the highest validation silhouette wins.
- **Anomalies:** Isolation Forest on the `anomaly` feature set. Operating assumption:
  1% of readings flagged; the threshold is the 99th percentile of validation scores and
  is not refitted on test.

## Comparison on validation

| Feature set | Candidate | Silhouette | Bootstrap ARI | Temporal ARI |
| --- | --- | --- | --- | --- |
| regime | **kmeans** | **0.823** | **0.999** | **0.999** |
| regime | gmm_diag | 0.758 | 1.000 | 0.841 |
| regime | gmm_full | 0.758 | 1.000 | 0.836 |
| regime_with_calendar | kmeans | 0.384 | 0.998 | 0.995 |
| regime_with_calendar | gmm_diag | 0.347 | 0.664 | 0.875 |
| regime_with_calendar | gmm_full | 0.288 | 0.496 | 0.416 |

Adding calendar inputs makes the GMMs unstable (bootstrap ARI 0.66 and 0.50). The
silhouette also falls by half, but the two feature sets have 5 and 10 dimensions, so
those silhouettes are not strictly comparable; the stability result carries the
decision. Selecting by silhouette also tends to favour K-Means over GMM.

## Selected regimes

Regimes are named by electrical signature (`order_by_profile`), not by usage rank,
because the two idle regimes have almost the same usage.

| Regime | Median usage | Signature | When |
| --- | --- | --- | --- |
| idle, inductive | ~3.2 kWh | lagging reactive energy, lagging PF ~60% | night |
| idle, capacitive | ~3.9 kWh | **leading** reactive energy, leading PF ~22% | pauses within working hours |
| production | ~61 kWh | lagging PF ~92% | working hours |

The capacitive regime suggests reactive-power compensation stays switched on when load
drops during the day.

## Serialized bundle

`artifacts/models/final_model.joblib` stores a `ModelBundle` with both fitted
preprocessors, the regime model, the regime naming map, the Isolation Forest, the
validation threshold, the `transition_filter` flag (on since v1.1, see
[Evaluation](evaluation.md#transition-filter-model-v11)), and metadata (data hash,
versions, selection reason).
`ModelBundle.predict` accepts a snake_case frame in the UCI layout and ignores
`Load_Type` if present. It returns `is_anomaly_raw` (score above threshold),
`regime_boundary` (computed in chronological order from `timestamp` or `date`, never
across gaps) and `is_anomaly` (raw flag, minus boundaries when the filter is on).

## Next anomaly comparison

The published Isolation Forest uses the `anomaly` contextual feature set and a threshold
calibrated to the top 1% of validation scores (0.6247), rather than a fixed
`contamination` parameter. Post-hoc tracking by `Load_Type` found uneven signal
concentration; this is not an error metric because load is not a failure label. A future
comparison may test alternative contextual scoring, but thresholds and alert persistence
must be frozen outside the data used for reporting.

A future supervised `Load_Type` classifier has a separate purpose: predict the known
regime and be evaluated with a temporal split, macro-F1, and balanced accuracy. It does
not turn `Load_Type` into a failure label or validate anomaly detection.

## Deferred candidates

DBSCAN/HDBSCAN, hierarchical clustering, K-Medoids, spectral clustering, SOM, UMAP,
autoencoders, LOF, One-Class SVM, and robust covariance remain documented alternatives.
The selected baseline met every protocol criterion, so none was needed to answer a
specific failure.
