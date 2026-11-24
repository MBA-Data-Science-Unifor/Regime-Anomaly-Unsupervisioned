# Exploratory Analysis

The implemented EDA is recorded in artifacts/notebooks/01_EDA.ipynb.

## Structure

1. data contract, quality, and generated dictionary;
2. univariate numerical, categorical, and temporal analysis;
3. feature relationships with Load_Type excluded;
4. PCA and t-SNE projections;
5. skewness, IQR, Spearman, and day-hour diagnostics;
6. three-regime K-Means and GMM baselines;
7. exploratory Isolation Forest signals and their post-hoc `Load_Type` tracking;
8. rationale for selected and deferred techniques.

## Interpretation rules

- Load_Type supplies only the number three and its descriptive frequency;
- projections do not define clusters;
- elbow, silhouette, AIC, and BIC are diagnostics, not automatic selectors;
- IQR extremes are not equivalent to anomalies;
- Isolation Forest signals are not confirmed incidents;
- `Load_Type` may be cross-tabulated only after fitting to describe signal concentration;
  it neither fits nor validates the detector.

## Generated outputs

The notebook writes a data dictionary, CSV summaries, and 21 PNG figures under
artifacts. These outputs are intentionally ignored by Git and must be regenerated
locally. Stable quantitative impressions are summarized in [Initial Findings](initial-findings.md).

The documentation publishes compact, reproducible versions of the correlation,
month-hour consumption, K-Means diagnostic, and post-hoc signal-tracking figures. They
can be regenerated with:

    python scripts/generate_docs_figures.py

Each figure is accompanied by an interpretation boundary in
[Initial Findings](initial-findings.md); the images are evidence, not standalone proof of
causality or business validity.
