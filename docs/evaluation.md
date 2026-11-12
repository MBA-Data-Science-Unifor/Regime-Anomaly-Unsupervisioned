# Evaluation

Evaluation is not performed in the EDA. It must use a frozen protocol and distinguish
regime geometry, stability, anomaly ranking, and optional external agreement.

## Internal clustering evidence

- silhouette;
- Davies–Bouldin;
- Calinski–Harabasz;
- cluster-size balance;
- resampling and seed stability;
- temporal stability and centroid drift.

## Probabilistic and anomaly evidence

- GMM likelihood, AIC/BIC diagnostics, and assignment uncertainty;
- Isolation Forest score distribution and sensitivity to contamination;
- stability of the top-ranked anomaly set;
- review by time window and operating context.

## External evaluation, later only

After model choices are frozen, Load_Type may support agreement measures such as ARI,
NMI, contingency tables, and regime interpretation. These are not supervised training
metrics and must not influence the unsupervised fit.

If a later supervised task is approved, it requires a separate objective, split,
baseline, and metrics. Accuracy alone is insufficient for imbalanced categories.

## Guardrails

PCA/t-SNE plots never replace metrics in the original transformed space. Thresholds
cannot be selected on the same data used for final reporting. Current EDA values are
preliminary.
