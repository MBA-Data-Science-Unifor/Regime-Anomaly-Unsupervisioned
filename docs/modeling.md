# Modeling

Final modeling belongs in artifacts/notebooks/03_Modeling.ipynb. Algorithms shown in the
EDA are baselines, not a selected production model.

## Current hypothesis

Primary regime models use exactly three groups, derived from the number of Load_Type
categories without using their identities during fitting.

## Baselines carried forward

- K-Means for scalable, interpretable centroid profiles;
- three-component diagonal-covariance GMM for probabilistic overlap;
- Isolation Forest for global anomaly scoring.

## Deferred candidates

DBSCAN/HDBSCAN, hierarchical clustering, K-Medoids, spectral clustering, SOM, UMAP,
autoencoders, LOF, One-Class SVM, and robust covariance methods remain documented
alternatives. They should be introduced only when their assumptions answer a specific
failure of the baselines.

## Required experiment record

Every experiment must record data hash, time split, feature set, fitted preprocessing,
algorithm, parameters, seed, runtime, internal metrics, stability, cluster sizes,
temporal drift, and limitations. The final model must be serialized with preprocessing
under artifacts/models and accompanied by metadata.
