# Data Source

## Dataset

The project uses the **RT-IoT2022** dataset, available locally at:

```text
artifacts/data/raw/RT_IOT2022
```

The code does not download the raw file automatically, and notebooks must not modify
it. Derived data must be written to `artifacts/data/processed/`.

## General contents

The dataset describes IoT network flows. Its fields include:

- source and destination ports;
- protocol and service;
- flow duration;
- packet counts and rates;
- header and payload sizes;
- protocol flags;
- inter-arrival times;
- windows and active and idle periods;
- the traffic type recorded in `Attack_type`.

## Provenance and versioning

Before the model is published, the project must record the following in its manifest:

- official source and bibliographic reference;
- acquisition date;
- license and terms of use;
- file size and SHA-256 hash;
- version used in the analysis.

These details still need to be consolidated; there is no final manifest at this stage.
