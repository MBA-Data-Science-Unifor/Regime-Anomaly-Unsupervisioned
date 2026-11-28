# Evaluation

The base model was evaluated on November–December after the model, preprocessing and
anomaly threshold were fixed. Earlier exploratory analysis covered the full year, so
this is not a fully independent test. Values come from `artifacts/metadata/final_metrics.json`.

## Internal evidence on test

| Metric | Validation | Test |
| --- | --- | --- |
| Silhouette | 0.823 | 0.768 |
| Davies–Bouldin | 0.261 | 0.332 |
| Smallest group share | 21.3% | 24.3% |
| Alert rate (target 1%) | 1.00% | 0.84% |

Regime shares stay close across periods: idle inductive 38% / 42% / 41%, idle
capacitive 24% / 21% / 24%, production 38% / 37% / 34% (train / validation / test).

Mean silhouette by regime on validation / test was 0.921 / 0.813 (idle inductive),
0.889 / 0.843 (idle capacitive), and 0.670 / 0.662 (production), on samples of
5,000 readings per split. These internal measures do not establish operational truth.


# Anomaly evidence

- the Isolation Forest threshold is 0.6247: the 99th percentile of validation scores;
- the top 1% on validation overlaps 87% on average across five seeds (Jaccard), which
  supports reproducibility of the highest-ranked signals;
- around 40% of validation alerts recur at the same weekday and time in three or more
  weeks, so recurrence is operational context rather than proof of a fault.

- the 1% rate is an operating assumption: there are no fault labels to estimate it.

## External agreement with Load_Type

Notebook 03 compares all fitted K-Means and GMM candidates with `Load_Type` using
ARI and NMI, as well as accuracy, balanced accuracy and macro F1 after mapping each
cluster to its most frequent training label. Multiple clusters can map to the same
class. This post-hoc comparison does not train or select the clustering models.
Calendar features change the question and may improve label agreement without
improving electrical regime discovery. The historical test is not independent.

Notebook `03_Modeling.ipynb` includes a separate supervised KNN experiment. The
configuration selected on validation uses calendar features and 15 neighbors: macro F1
is 0.919 on validation and 0.593 on the historical test. Test accuracy is 69.9%,
versus 53.1% for the training-majority baseline. Recall is 93.6% for Light_Load,
36.4% for Maximum_Load, and 47.9% for Medium_Load. The decline between periods
requires investigation; prior full-year exploration limits test independence. This
classifies an already measured interval and does not validate anomaly detection.
Notebook 04 additionally compares alternatives: Extra Trees with calendar features
reached validation macro F1 0.954, but test macro F1 was 0.593, approximately the
same as KNN. Removing one correlated feature changed validation silhouette from 0.821
to 0.827 in a different feature space; this does not by itself justify replacement.

Mapping each cluster to its most frequent training label gives test accuracy 59.6%,
balanced accuracy 55.9%, and macro F1 54.0%, versus 53.1% for the majority training
class. One-vs-rest AUC is 0.881 for Light_Load, 0.708 for Maximum_Load, and 0.749
for Medium_Load. Scores are training class proportions within each cluster, not
calibrated probabilities. These results concern Load_Type, not fault detection; no
fault labels are available for anomaly precision or ROC.

| Reference on test | ARI | NMI |
| --- | --- | --- |
| selected model (`regime` / K-Means) | 0.342 | 0.304 |
| sensitivity (`regime_with_calendar` / K-Means) | 0.355 | 0.315 |
| calendar majority rule (hour × week status, uses train labels) | 0.494 | 0.342 |

Agreement is moderate and below a pure calendar rule. This is expected: Load_Type is a
time-of-use tariff schedule, while the regimes describe the plant's electrical state.
The model separates idle from production but does not split Medium from Maximum load,
which are both production electrically (92% of the idle-inductive regime is
`Light_Load`).

!!! note "Protocol deviation"
    The protocol specified the calendar reference with hour, week status **and month**.
    November and December are absent from training, so that rule collapses to a
    constant (ARI = 0). The reference uses hour and week status. This affects only the
    reference, not model selection, which was already frozen.

`Load_Type` may also be used in a post-hoc table to describe which load regimes occur
among signals. That table is not an anomaly metric: it must not calibrate the threshold,
equalize class rates, or turn an alert into a confirmed failure.

## Transition filter (model v1.1)

Section 10 of notebook 03 suppresses alerts on regime boundaries, keeping the v1.0 threshold. The
decision rule required boundary alerts to be at least 3× the boundary reading share on
validation; the observed lift was 9.5×. The rule was written after notebook 04 had
already shown that 88% of validation alerts (90% on test) fall on boundaries, so it
documents the decision rather than testing it blind.

| Split | Alerts v1.0 | Alerts v1.1 | Rate v1.1 |
| --- | --- | --- | --- |
| validation | 59 | 7 | 0.12% |
| test | 49 | 5 | 0.09% |

Ten of the 12 remaining alerts share one signature: medium load (10–31 kWh) with
leading current on weekend mornings, the same profile as the 22 May episode. The other
two are also weekend readings at medium load: Saturday 6 October 12:30 (production
regime, 24 kWh) and Sunday 21 October 16:30. In the July night episode,
7 of 29 alerts are suppressed because the event itself creates regime changes; 22 remain.
Recalibrating the threshold on non-boundary readings instead would produce 54 validation
alerts, mostly marginal.

Caveats: the recurrence analysis and the boundary shares in notebook 04 looked at the
whole year, test included, before this change was made, so the v1.1 test figures are
not an independent evaluation of the filter; and in continuous operation an alert is delayed by
15 minutes, because a boundary needs the next reading. `is_anomaly_raw` and
`anomaly_score` remain published.

## Guardrails respected

- Load_Type never entered a fit and was used for agreement only after freezing. It was
  inspected on train only, in notebook 02, and that inspection did shape one design
  choice: excluding calendar features from the regime set (D3). This is a deliberate,
  disclosed use of the label before freezing;
- the anomaly threshold was chosen on validation and reported on test;
- PCA/t-SNE were not used for selection; all metrics are in the transformed space.

## Limitations

- one year of data, so seasonality cannot be validated across cycles;
- regime names come from profile interpretation and need validation with plant staff;
- no fault labels: anomaly precision cannot be measured.
