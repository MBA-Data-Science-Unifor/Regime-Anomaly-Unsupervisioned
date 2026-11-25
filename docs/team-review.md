# Team Review

Three pending items depend on people, not code. This page and
`artifacts/notebooks/04_Review.ipynb` prepare each one so it can be decided in a single
meeting. The notebook only reads published artifacts; nothing is refitted.

Time convention: each reading covers 15 minutes. Times below are shown as intervals
(`12:00–12:15`), the period the reading measures.

## 1. Decisions for approval (project team)

| # | Decision | Evidence | If rejected |
| --- | --- | --- | --- |
| D1 | Move the 24:00 reading to the next midnight | 365 backward jumps with a naive parse | no valid alternative; ordering and split break |
| D2 | Chronological split Jan–Aug / Sep–Oct / Nov–Dec | adjacent readings are dependent | redo notebooks 02 and 03 |
| D3 | Calendar **excluded** from regime features | a calendar majority rule reproduces ~92% of training Load_Type (in-sample, ~1,500 slots; hour + week status + month alone: 87%); with calendar, GMMs become unstable (silhouette 0.82 → 0.38, but measured in 5 vs 10 dimensions, so not strictly comparable) | switch to `regime_with_calendar` (already measured) |
| D4 | CO2 excluded | Pearson 0.99 with usage, eight distinct values | usage weighs double in distances |
| D5 | `log1p` energy, `log1p(100 − PF)` power factor | usage skewness 1.14 → 0.43 | redo selection |
| D6 | Extremes kept | anomalies are a project goal | detector loses the unusual cases |
| D7 | Selection rule (bootstrap ARI ≥ 0.80, smallest group ≥ 5%, best silhouette) | fixed before results | result unchanged: K-Means also leads on temporal stability |
| D8 | 1% alert rate calibrated on validation | 0.84% on test; Jaccard 0.87 across seeds | change `ALERT_RATE` in notebook 03 |
| D9 | Calendar reference without month (protocol deviation) | Nov–Dec absent from training | affects the reference only |

D3 and D8 change how results are read the most.

## 2. Regime names (plant staff)

The evidence supports the three names:

- **idle, inductive** — one long, regular night block (median episode 9.75 h), no leading
  current;
- **idle, capacitive** — short episodes, 496 of 838 between two production blocks
  (pauses, peaking at 12:00 on weekdays) and 267 between production and the night block
  (end of shift); covers much of the day at weekends;
- **production** — weekday working hours (~94% of readings from 08:00 to 17:00, except
  12:00–13:00).

**Leading current follows the clock, not the load.** Among low-load readings
(< 10 kWh), leading current is present in 0% before 08:30, 35% in 08:30–08:45, 100% from
08:45–09:00 until 21:45–22:00, 65% in 22:00–22:15, and 3% after. At night, with the same
load, it appears in only 1.4%. This is consistent with reactive-power compensation
(a capacitor bank) switched on a timer from about 08:40 to 22:05.

**Questions for plant staff**

1. Is there a scheduled break around 12:00–13:00 on weekdays?
2. Is the capacitor bank switched by timer, roughly 08:40–22:05, including weekends?
3. Does the plant run partially during the day on Saturdays and Sundays?
4. Do the names fit, or are there better internal terms (e.g., "night shutdown",
   "compensated standby")?

If question 2 is confirmed, the capacitive regime is an **over-compensation** window: the
capacitors stay on while load is low, which may be billed as excess leading reactive
energy.

## 3. Alert triage (operations)

Each alert gets two objective marks:

- **boundary** — its regime differs from the previous or next reading;
- **recurring** — the same weekday and interval alerted in at least three distinct weeks.

**Most alerts are regime transitions.** Boundary readings are 11.1% of all readings but
81.3% of alerts (88% on validation, 90% on test). A 15-minute reading that spans a state
change sits halfway between both states and looks unusual. The two most frequent
patterns are the capacitor switching off (22:00–22:15, up to 32 weeks) and the start of
the weekday break (12:00–12:15, 20–29 weeks).

| Priority | Suggested category | Alerts | Train | Validation | Test |
| --- | --- | --- | --- | --- | --- |
| 1 | isolated — investigate | 38 | 36 | 2 | 0 |
| 2 | recurring pattern | 70 | 60 | 5 | 5 |
| 3 | one-off transition | 50 | 30 | 13 | 7 |
| 4 | scheduled transition | 421 | 345 | 39 | 37 |

Training scores are in-sample (the Isolation Forest was fitted on train), so the
training alert rate (~2%) is not comparable with validation and test (~1%).

**The isolated alerts form two episodes worth investigating:**

- **15–23 July, 02:15–03:00** — leading current at night on most nights, outside the
  capacitor schedule. Candidate: compensation left on overnight for about a week
  (timer change, maintenance, or fault);
- **22 May, 09:00–10:00** — medium load (~25 kWh) with leading current.

**Triage sheet.** `artifacts/tables/revisao_alertas_triagem.csv` lists all 579 alerts by
priority and score, with an empty `parecer_operacao` column. Allowed values: `rotina`
(known scheduled event), `transicao` (normal state change), `falha` (real equipment or
process problem), `investigar` (unknown), `dado` (measurement or recording error).
Once filled, the detector's precision can be measured for the first time.

## Transition filter (applied in v1.1)

Section 10 of notebook 03 applies the boundary filter: 59 → 7 validation alerts and 49 → 5 test
alerts. The triage sheet keeps all 579 unfiltered alerts so operations can still confirm
that transitions are of no interest; if they are, republish with
`transition_filter=False`.
