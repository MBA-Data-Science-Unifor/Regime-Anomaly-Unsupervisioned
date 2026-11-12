# Exploratory Analysis

The implemented EDA is recorded in artifacts/notebooks/01_EDA.ipynb.

## Structure

1. data contract, quality, and generated dictionary;
2. univariate numerical, categorical, and temporal analysis;
3. feature relationships with Load_Type excluded;
4. PCA and t-SNE projections;
5. skewness, IQR, Spearman, and day-hour diagnostics;
6. three-regime K-Means and GMM baselines;
7. exploratory Isolation Forest signals;
8. rationale for selected and deferred techniques.

## Interpretation rules

- Load_Type supplies only the number three and its descriptive frequency;
- projections do not define clusters;
- elbow, silhouette, AIC, and BIC are diagnostics, not automatic selectors;
- IQR extremes are not equivalent to anomalies;
- Isolation Forest signals are not confirmed incidents;
- no supervised estimator or label-based metric belongs in the EDA.

## Generated outputs

The notebook writes a data dictionary, CSV summaries, and 20 PNG figures under
artifacts. These outputs are intentionally ignored by Git and must be regenerated
locally. Stable quantitative impressions are summarized in [Initial Findings](initial-findings.md).
