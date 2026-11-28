# PBL canvas — problem, data and decisions

This canvas answers the 11 project questions. It distinguishes observed evidence from
interpretation and proposed targets. This is an academic analysis of a public dataset,
not a contracted or approved plant deployment.

| Team | Track |
| --- | --- |
| Alexandre Franco — data analysis and modeling; Rodrigo Franco — data engineering; Caio Cunha Franco — AI engineering. | Energy analysis, clustering and anomaly detection, with a separate supervised comparison. **Official track name:** not provided; confirm with the team. |

## 1. Business context

The UCI source describes electricity readings from DAEWOO Steel Co. Ltd in Gwangyang,
South Korea. Potential users include energy analysts and plant operations. The project
team decides the analytical method; an actual plant team would decide whether profiles
and alerts are useful. Its real decision makers and authority are unknown.

## 2. Pain point

Without organized energy profiles, analysts may find it difficult to distinguish
recurring patterns from readings worth investigating and may receive many transition
alerts. This is a hypothesis: we have not established that the company lacks a
segmentation process, currently has this problem, or incurs a financial loss.

## 3. Business objective

Support understanding of energy behavior and prioritization of unusual readings for
review. Energy savings, failure reduction and financial benefit have not been measured;
the proposed objective needs agreement from operational stakeholders.

## 4. Business success criteria

No executive target has been approved. A proposed pilot would review the **20 highest
scoring retained alerts** in a period yet to be defined, or all if fewer than 20, and a sample of non-alert readings,
recording an assessment for **100% of selected cases**. This measures triage
completion, not detector quality. Report useful alerts divided by reviewed alerts;
agree the minimum useful rate, non-alert sampling method, deadline and owner before the
pilot. Meaningful precision and recall require appropriate labels and sampling.

## 5. Data-mining goal

- Cluster electrical profiles with K-Means and GMM; three groups are specified using
  the known cardinality of `Load_Type`, without using label values to fit the clusters.
- Rank unusual readings with Isolation Forest for investigation, documenting the
  threshold and transition filter.
- Compare supervised KNN and alternatives for classifying `Load_Type` after the same
  interval is measured; this uses training labels and does not validate faults.
- Use PCA and t-SNE for exploratory visualization, not to establish the group count.

## 6. Technical success criteria

| Criterion | Project rule | Observed result or status |
| --- | --- | --- |
| Groups | Exactly 3 in the principal hypothesis. | Specified by design. |
| Smallest group | At least 5% on validation. | K-Means: 21.3%. |
| Bootstrap stability | Mean ARI at least 0.80. | K-Means: 0.999. |
| Silhouette | Highest among eligible principal-feature candidates; no absolute minimum was specified. | K-Means: 0.823 validation, 0.768 historical test. |
| Anomaly alerts | Validation 99th-percentile threshold, approximately 1% raw alerts. | 59/5,856 on validation; this is an assumption, not precision or a validated noise limit. |
| Supervised classification | Compare macro F1 and class-level results with time-aware references; no approved minimum target. | KNN macro F1: 0.919 validation, 0.593 historical test. |

No validated maximum false-positive rate is available without fault labels and agreed
costs. EDA covered the full year and the filter was considered after test inspection;
the historical test is not fully independent. A later independent evaluation remains
open. See [Evaluation](../evaluation.md).

## 7. Unit of analysis

Each row is one 15-minute electrical reading with calendar context and `Load_Type`.
Source timestamps denote the interval end; day-closing `00:00` rows are moved to the
following midnight for chronological order. Nearby readings are dependent.

## 8. Data source and volume

The [UCI Steel Industry Energy Consumption dataset](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption)
(DOI 10.24432/C52G8C) contains **35,040 rows and 11 columns** for 2018. The corrected
timestamps run from 2018-01-01 00:15 to 2019-01-01 00:00. Training contains 23,328
readings, validation 5,856 and test 5,856; day-closing readings remain with the day
they close. Preparation metadata reports no missing values, duplicate timestamps or
irregular intervals after correction. The source states **CC BY 4.0**; retain
attribution and follow its terms. Dataset licensing is not authorization to operate
the plant. See [Data Source](../data-source.md).

## 9. Data-oriented questions

1. On September–October 2018, do the three selected electrical groups have a smallest
   share ≥ 5%, what is their silhouette, and how stable are bootstrap fits on training?
2. How do group shares change, in percentage points, across January–August,
   September–October and November–December 2018?
3. With the threshold calibrated to 1% raw alerts on validation, how many alerts occur
   before and after filtering, and at boundaries, in validation and historical test?
4. With the cluster-to-class mapping learned on January–August, what are test ARI and
   macro F1 against `Load_Type`, compared with supervised classification and the
   training-majority baseline?
5. In a proposed pilot, what proportion of selected cases receives an assessment and
   what proportion of reviewed alerts is useful? The pilot deadline, usefulness target
   and non-alert sampling plan remain to be agreed, so this is not fully SMART yet.

The first four refer to the historical 2018 data; none establishes fault-detection
quality. See [Evaluation](../evaluation.md) for results and limitations.

## 10. Constraints and risks

- Budget, delivery deadline and operating costs have not been specified or approved.
- One year and one plant do not establish generalization; nearby readings are dependent.
- The test has already been exposed. The alert rate is an assumption, not fault recall.
- The transition filter can suppress relevant events and may require the next reading,
  introducing a potential 15-minute delay. Synthetic cases are not verified failures.
- Respect CC BY 4.0 attribution; no internal company requirements have been established.
  Do not infer personal responsibility from these readings.
- Regime names and physical explanations are hypotheses, not proof or authority for
  automated operational action.

## 11. Expected action by group

| Result | Proposed action | Validator or decision maker |
| --- | --- | --- |
| Idle inductive | Check whether the low-consumption night profile and name are appropriate. | Plant operations, if available. |
| Idle capacitive | Investigate whether reactive compensation remains on during pauses or specific hours. | Operations and electrical staff, if available. |
| Production | Examine the higher-consumption profile and differences across periods. | Energy analyst and operations. |
| Retained raw alert | Prioritize for review and record an assessment, without automatic maintenance. | Operations. |
| Alert suppressed at a boundary | Review a sample and decide whether the filter should remain enabled. | Operations. |
| Predicted `Load_Type` | Compare to observed labels, especially medium versus maximum errors. | Data team; operational use needs approval. |

These are proposed actions, not decisions approved by the company. See the
[PBL Board](pbl-board.md) for open work.
