# Problem Understanding

## Context

IoT devices produce heterogeneous network flows and may be either targets or vectors
of attacks. This project studies recurring patterns and unusual observations in the
RT-IoT2022 dataset without assuming in advance which algorithm will become the final
model.

## General objective

Build a reproducible analysis that helps distinguish traffic behaviors, investigate
anomalies, and eventually test a model through a web application.

## Guiding questions

- Which features best describe the dataset's flows?
- Are there natural traffic regimes or clusters?
- Which observations deviate from the identified patterns?
- How can the available labels be used to evaluate usefulness without leakage?
- Which errors are more costly: false positives or undetected attacks?

## Current scope

The project is under development. There is no selected model, operational threshold,
final metric, or deployment recommendation yet.

## Out of scope at this stage

- automatic traffic blocking;
- automated incident response;
- guaranteed generalization to another network;
- causal diagnosis of attacks;
- production deployment.
