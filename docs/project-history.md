# History of findings and decisions

This retrospective record brings together the main findings and decisions in logical
order. It does not assign unrecorded dates or claim an exact decision chronology.
Figures refer to the artifacts available during the review and may change on a rerun.
See [Evaluation](evaluation.md) and [Team Review](team-review.md) for current details.

## Data and exploration

- The dataset contains 35,040 fifteen-minute readings from 2018. The source's `00:00`
  reading closes the stated day; moving it to the following midnight restores
  chronological order.
- CO₂ was excluded from the main model inputs because it is almost linearly associated
  with consumption. Extreme values were retained for anomaly investigation.
- The EDA examined the entire year. November–December was reserved during modeling,
  but it is not a fully independent test period.

## Preparation and regimes

- The temporal split uses January–August for training, September–October for
  validation and November–December for testing. Transformations and models are fitted
  on training; the anomaly threshold is calibrated on validation.
- Three groups were specified using the cardinality of `Load_Type`, an external
  constraint on unsupervised clustering. Inspection of training labels also informed
  the decision to exclude calendar features from the main regime inputs.
- K-Means on electrical variables was selected, with validation silhouette 0.823 and
  mean bootstrap ARI 0.999. These are internal indicators, not proof of operational
  states. The names idle inductive, idle capacitive and production require plant review.

## Anomalies and transition filter

- The Isolation Forest threshold is the validation score's 99th percentile. The 1%
  target is an operating assumption; fault labels are unavailable to measure detector
  precision or recall.
- Of 59 raw validation alerts, 52 fell on regime boundaries, a concentration around
  9.5 times the boundary share of readings. The v1.1 filter reduced validation alerts
  from 59 to 7 and test alerts from 49 to 5. Raw alerts and scores remain available.
- The filter was motivated after reviewing evidence that included the test period, so
  its test figures are not a blind independent evaluation. Full-year recurrence is
  retrospective; online recurrence must use only observations available at the time.
  Operations must still decide whether suppressing boundary alerts is appropriate.

## Quality review and external agreement

- Global silhouette was 0.823 on validation and 0.768 on test; the production regime
  had the lowest per-regime means, 0.670 and 0.662 respectively.
- Mapping clusters to their most frequent training `Load_Type` gave test accuracy
  59.6%, balanced accuracy 55.9%, and macro F1 54.0%, against a 53.1% majority-class
  baseline. Recall for `Medium_Load` was 33.4%.
- ROC scores are training class proportions within each cluster, not calibrated
  probabilities. They measure agreement with `Load_Type`, not fault detection. See
  [Evaluation](evaluation.md) for the detailed metrics and limitations.

## Open work

1. Ask operations to validate regime names, highlighted episodes and the transition
   filter.
2. Obtain assessments of alerts and a sample of non-alerted readings to support a more
   complete fault evaluation.
3. Evaluate frozen decisions and thresholds on a later, previously unseen period.
4. For online use, account for the next reading needed to identify a boundary and
   calculate recurrence without future observations.

## Team and responsibilities

| Member | Project role | Reported responsibilities |
| --- | --- | --- |
| Alexandre Franco | Data Analyst and Modeling | Data analysis and application of models, including unsupervised techniques. |
| Rodrigo Franco | Data Engineer | Data engineering. |
| Caio Cunha Franco | AI Engineer | Artificial intelligence engineering. |

These roles reflect the responsibilities reported by the team and can be expanded as
individual contributions are documented.
