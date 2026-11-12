# Problem Understanding

## Context

Industrial electricity demand varies with production intensity, reactive power,
calendar effects, and equipment behavior. Understanding recurring operating regimes can
support energy planning and help prioritize unusual measurements for investigation.

## Objective

Build a reproducible unsupervised analysis of the Steel Industry Energy Consumption
dataset that:

- describes energy and power-factor behavior;
- investigates structure compatible with three operating regimes;
- signals unusual observations without claiming a fault diagnosis;
- prepares evidence for later model comparison and a read-only application.

## Guiding questions

- Which variables best distinguish low, medium, and high operating behavior?
- Are the three expected regimes geometrically coherent without using their labels?
- How do hour, weekday, and weekend behavior affect the regimes?
- Which observations are globally unusual?
- Which findings remain stable across time and resampling?

## Boundaries

The work does not infer causality, equipment failure, financial savings, or production
quality. Load_Type values are not used for unsupervised fitting. No supervised model,
operational threshold, or production recommendation is approved at this stage.
