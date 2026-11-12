# Initial Findings

!!! warning "Exploratory evidence"
    These observations come from the current EDA and regenerated local artifacts.
    They are not frozen evaluation results or production recommendations.

## Dataset profile

- 35,040 measurements and 11 columns;
- no missing or exact duplicate rows;
- 15-minute frequency across 2018;
- 25,056 weekday and 9,984 weekend observations;
- Load_Type counts: 18,072 Light_Load, 9,696 Medium_Load, and 7,272 Maximum_Load.

## Distribution impressions

Usage, lagging reactive energy, leading reactive energy, and CO2 are right-skewed.
Leading power factor is strongly left-skewed. The IQR rule marks about 23.8% of leading
power-factor observations and 22.1% of leading reactive-energy observations as extreme;
this reflects distribution shape and must not be interpreted as the same thing as an
operational anomaly.

## Relationship impressions

The current Spearman diagnostics show:

- strong positive association between Usage_kWh and CO2, approximately 0.88;
- positive association between usage and lagging reactive energy, approximately 0.64;
- strong inverse association between leading reactive energy and leading power factor,
  approximately -0.97;
- clear hour-of-day and weekday/weekend structure in mean consumption.

These relationships motivate scaling, redundancy checks, and temporal stability tests.

## Multivariate impressions

The first two PCA components explain approximately 73.4% of transformed-space variance.
PCA and t-SNE show structured regions, but projections do not prove the existence or
business meaning of clusters.

For K-Means diagnostics on a reproducible sample, K=3 has the highest tested silhouette,
approximately 0.449. The full three-cluster baseline currently contains 13,074, 14,378,
and 7,588 observations. This supports continued investigation but is not external
validation.

For the GMM diagnostic, BIC continues improving through eight tested components while
the problem-constrained model remains fixed at three. This suggests statistical
substructure inside the three operational regimes rather than evidence that the business
problem has eight regimes.

Isolation Forest flags 701 observations under an assumed contamination rate of 2%.
Those records are investigation candidates, not confirmed faults.

## Next checks

- reproduce preparation outside the EDA notebook;
- measure cluster stability under resampling and time splits;
- test sensitivity to feature groups and transformations;
- define a frozen external-evaluation protocol;
- resolve the CO2 unit wording;
- avoid turning exploratory labels into supervised training prematurely.

