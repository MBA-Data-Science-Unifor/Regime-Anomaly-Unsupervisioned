# Data Preparation

Preparation is implemented in `artifacts/notebooks/02_preprocessing.ipynb`, which records
the evidence, and in `src/regime_anomaly/preprocessing.py`, which holds the reusable logic.

!!! warning "Proposed decisions"
    The choices below are evidence-based proposals pending team approval.

## Pipeline

1. **Timestamp repair.** Readings are stamped at the end of their 15-minute interval.
   The reading that closes each day (24:00) is stored after 23:45 with the same calendar
   date and `NSM = 0`, so a naive parse places it 24 hours early (365 backward jumps).
   These rows move to the following midnight; the series becomes a continuous
   15-minute grid from 2018-01-01 00:15 to 2019-01-01 00:00.
2. **Structural validation.** Execution stops on nulls, duplicated timestamps, frequency
   gaps, negative energy, power factor outside 0–100, or unknown calendar categories.
3. **Calendar features (row-local).** Sine/cosine of time of day (from `NSM`) and day of
   week, plus a weekend flag.
4. **Chronological split.** Train January–August (23,328 rows), validation
   September–October (5,856), test November–December (5,856). A reading stamped exactly
   on a boundary closes the earlier period and stays on that side. The test period is
   frozen until final evaluation.
5. **Transformations, fitted on train only.** `log1p` on energy variables,
   `log1p(100 − PF)` on power factors, then `StandardScaler`.

## Feature sets

| Set | Inputs | Purpose |
| --- | --- | --- |
| `regime` | 3 energy + 2 power-factor variables | main regime clustering |
| `regime_with_calendar` | `regime` + 5 calendar features | sensitivity analysis |
| `anomaly` | `regime` + time of day + weekend flag | contextual anomaly detection |

## Key evidence

- **Load_Type behaves like a time-of-use schedule.** From 00:00 to 08:59 it is always
  `Light_Load`, and a majority rule on time of day, week status, and month reproduces
  about 92% of training labels. Calendar inputs would let clusters rebuild the tariff
  table, so the main regime set excludes them and uses calendar only to describe clusters.
- **CO2 is excluded** from all feature sets: Pearson ≈ 0.99 with usage, only eight
  distinct values, 58% zeros. It stays available for profiling.
- **Extremes are kept.** Finding unusual observations is a project goal; clipping would
  erase that signal.
- **Drift exists.** Median usage is about 23% lower in validation than in training, so
  validation also measures temporal robustness.

## Leakage boundary

Load_Type is never a feature (`assert_no_label` guards every feature set). It was
inspected on the training period only, to understand its meaning, and is otherwise
reserved for external assessment. Fitted transformers are not serialized during
preparation; notebook 03 refits them on train and stores them with the final model.

## Outputs (regenerated locally, not versioned)

- `artifacts/data/processed/prepared_dataset.csv`
- `artifacts/metadata/preprocessing.json` (raw-file SHA-256, boundaries, feature sets,
  quality report, library versions)
- `artifacts/tables/preprocessamento_*.csv` and figures `21`–`24` in `artifacts/images/`

## Decisions still open

- leading kVarh and leading power factor keep a large mass at their limit (0 / 100%);
  test a binary "at limit" indicator;
- redundancy of the leading kVarh × leading power-factor pair (Spearman ≈ −0.97);
- anomaly threshold calibration on validation instead of a fixed 2% contamination.
