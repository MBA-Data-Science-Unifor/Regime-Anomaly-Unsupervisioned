# Project Status

| Item | State |
| --- | --- |
| Steel Industry raw dataset | available locally |
| EDA notebook | implemented; review in progress |
| Preparation notebooks | 02 (configuration comparison) and 02b (protocol used by the model); decisions pending approval |
| Preprocessing module | `preprocessing.py` with tests |
| Modeling notebook | implemented with a protocol fixed before results |
| Selected model | K-Means, three regimes, electrical features only |
| Anomaly detector | Isolation Forest, 1% threshold calibrated on validation |
| Transition filter | v1.1: alerts on regime boundaries suppressed (59 → 7 on validation) |
| Frozen evaluation | complete on November–December |
| Serialized bundle | `final_model.joblib` with `ModelBundle.predict` and tests |
| Integrity manifest | `metadata/manifest.json` with SHA-256 per artifact and raw-data provenance; checked by `uv run regime-analysis` |
| Reproduction | `uv run invoke notebooks` runs 01–05 in order |
| Streamlit | monitoring dashboard (overview, monitoring, alerts, models, reports) reading published results, plus a page that runs the model on an uploaded CSV |
| MkDocs | updated through evaluation |

## Pending

Items 1–3 depend on people. Each is prepared in [Team Review](team-review.md) and
`artifacts/notebooks/04_Review.ipynb`.

1. **Team approval** of decisions D1–D9 (decision register ready);
2. **Plant staff** answers to four questions on regime names and the capacitor schedule
   (evidence ready);
3. **Operations** triage of 579 alerts in `revisao_alertas_triagem.csv`, starting with
   38 isolated alerts in two episodes (15–23 July nights, 22 May morning), and
   confirmation that regime transitions are of no interest (basis of the v1.1 filter);
4. record contribution history.

## Resolved

- **EDA timestamp handling.** Notebook 01 groups by the source date, which already
  assigns the 24:00 reading to the day it closes (verified for 100% of rows against the
  corrected timestamps). The chronological correction is needed only where order matters
  and is applied in notebook 02b; notebook 01 now documents this convention.
- **Reproducibility gaps.** `nbconvert` is now declared in the `analysis` group,
  `requirements.txt` is exported from `uv.lock` (it was a partial UTF-16 freeze without
  Streamlit or Plotly), and CI also checks formatting.
