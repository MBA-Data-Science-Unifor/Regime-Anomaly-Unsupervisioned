# Evaluation

Evaluation must distinguish geometric quality, detection capability, and operational
usefulness.

## Candidate metrics

For clustering:

- silhouette score;
- Davies-Bouldin index;
- Calinski-Harabasz index;
- resampling stability.

For detection evaluated against external labels:

- precision, recall, and F1 score;
- specificity and balanced accuracy;
- ROC AUC and PR AUC;
- confusion matrix;
- performance by traffic type.

## Considerations

- accuracy alone can be misleading for imbalanced datasets;
- the threshold must not be selected on the same set used to report performance;
- PCA or another visual projection does not replace metrics in the original space;
- available labels may not represent every real-world attack.

Final metrics have not yet been calculated or approved.
