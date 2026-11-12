# Data Understanding

## Unit of analysis

One row represents a 15-minute industrial energy observation. There are 35,040 rows,
which is consistent with 365 days times 96 intervals per day.

## Variable groups

| Group | Variables | Role |
| --- | --- | --- |
| Time | date, NSM | timestamp and seconds from midnight |
| Energy | Usage_kWh | active energy consumption |
| Reactive energy | lagging and leading kVarh | electrical behavior |
| Emissions | CO2(tCO2) | reported CO2 measure |
| Power quality | lagging and leading power factor | electrical efficiency/context |
| Calendar | WeekStatus, Day_of_week | operating context |
| External regime reference | Load_Type | cardinality and later evaluation only |

## Confirmed quality checks

- 35,040 rows and 11 columns;
- no missing values in the local CSV;
- no exact duplicate rows;
- 96 observations per complete day;
- three Load_Type categories;
- numerical variables have substantially different scales and asymmetric distributions.

## Important cautions

The UCI metadata and the CO2 column name use potentially inconsistent unit wording; the
data dictionary preserves the official metadata and this issue must be resolved before
final reporting. Date parsing uses day-first format. Load_Type is excluded from feature
relationships and model fitting.
