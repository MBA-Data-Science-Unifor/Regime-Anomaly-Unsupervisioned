# Data Source

## Dataset

The project uses **Steel Industry Energy Consumption**, published by the
[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption).

Local path:

    artifacts/data/raw/Steel_industry_data.csv

The project never downloads or edits the raw file automatically. Derived outputs belong
under artifacts/data/processed.

## Provenance

The measurements come from DAEWOO Steel Co. Ltd in Gwangyang, South Korea. The UCI
record reports 35,040 instances, no missing values, real and categorical features, and a
CC BY 4.0 license. The dataset citation is:

Sathishkumar V E, Changsun Shin, and Yongyun Cho (2021), Steel Industry Energy
Consumption, UCI Machine Learning Repository, DOI 10.24432/C52G8C.

## Measurement grain

Each row is a 15-minute observation during 2018. The fields cover active energy use,
lagging and leading reactive energy, CO2, power factors, seconds from midnight,
weekday/weekend context, day of week, and load type.

A future manifest must record the acquisition date, byte size, SHA-256 hash, UCI
identifier, DOI, and license.
