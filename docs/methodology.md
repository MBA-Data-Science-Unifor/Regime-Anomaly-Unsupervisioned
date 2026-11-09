# Methodology

The project follows an adaptation of CRISP-DM to organize the investigation while
keeping exploration, model selection, and final evaluation separate.

## Phases

1. **Problem understanding:** define users, the decision to support, risks, and criteria.
2. **Data understanding:** document the source, grain, schema, quality, and labels.
3. **Preparation:** split the data, handle data types, and prevent information leakage.
4. **Modeling:** compare unsupervised and novelty-detection approaches.
5. **Evaluation:** measure technical quality, stability, and operational usefulness.
6. **Publication:** save approved artifacts and make them available in Streamlit.

## Principles

- Decisions and metrics must be declared before final results are examined.
- Notebooks record the investigation; reusable code should move to `src/`.
- Tables, images, metrics, and models are published only under `artifacts/`.
- Streamlit reads artifacts but does not train models.
- Preliminary results must be clearly identified as such.

## Traceability

The change history, owners, and contributions will be added later. Until then, this
documentation records only the planned structure and decisions.
