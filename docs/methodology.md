# Methodology

The project follows CRISP-DM with an explicit separation between exploration,
unsupervised model development, and later external evaluation.

## Problem framing

The dataset contains three Load_Type values. Their count defines a structural hypothesis
of three operating regimes. Class identities are not used to fit preprocessing,
clustering, projections, or anomaly detection.

## Current phases

1. **Business understanding:** define the operational question and limits.
2. **Data understanding:** document source, grain, fields, quality, and time coverage.
3. **EDA:** inspect distributions, temporal patterns, correlations, projections, and
   unsupervised baselines.
4. **Preparation:** create a reusable, leakage-safe feature pipeline.
5. **Modeling:** compare candidate methods under a frozen protocol.
6. **Evaluation:** assess geometry, stability, temporal robustness, and only then
   optional agreement with external categories.
7. **Publication:** write approved artifacts and expose them read-only.

## Techniques used in the EDA

- Freedman–Diaconis histograms and IQR diagnostics for distributions;
- Pearson and Spearman for linear and monotonic association;
- calendar profiles for intraday and weekly structure;
- PCA for interpretable global projection;
- t-SNE for local-neighborhood visualization only;
- K-Means with K fixed at three as the centroid baseline;
- GMM with three components as a probabilistic counterpart;
- Isolation Forest as an exploratory anomaly baseline.

Elbow, silhouette, AIC, and BIC are diagnostics. They do not override the three-regime
problem definition.

## Techniques deferred

Density-based, hierarchical, spectral, medoid, neural representation, and alternative
anomaly methods are documented in the EDA notebook with their intended use, limitations,
and conditions for reconsideration. Supervised estimators and label-based metrics are
deliberately excluded from this phase.

## Reproducibility and publication

Seeds, transformations, parameters, and assumptions must be recorded. Notebooks are the
investigation record; approved reusable logic moves to src/regime_anomaly. Raw data,
figures, tables, models, and large derived files are regenerated locally and excluded
from Git.
