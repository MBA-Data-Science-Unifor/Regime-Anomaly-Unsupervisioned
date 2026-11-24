# Technical References

This page records the official references for the libraries and tools declared by the
project. Minimum versions come from `pyproject.toml`; the resolved environment is
recorded in `uv.lock`.

## Data and scientific computing

| Library | Project use | Official reference |
| --- | --- | --- |
| Python ≥ 3.12 | language and standard library | [Python documentation](https://docs.python.org/3/) |
| NumPy ≥ 2.5.4 | arrays, cyclic features, numerical checks, and notebook artifacts | [NumPy documentation](https://numpy.org/doc/stable/) |
| pandas ≥ 3.1.1 | CSV loading, tabular transformations, time series, and summaries | [pandas documentation](https://pandas.pydata.org/docs/) |
| scikit-learn ≥ 1.9.1 | preprocessing, PCA, K-Means, GMM, Isolation Forest, and metrics | [scikit-learn documentation](https://scikit-learn.org/stable/) |
| joblib ≥ 1.6.0 | serialization of preprocessing and model artifacts | [joblib documentation](https://joblib.readthedocs.io/en/stable/) |

The main scikit-learn APIs used in the notebooks are
[`ColumnTransformer`](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html),
[`StandardScaler`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html),
[`OneHotEncoder`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html),
[`PCA`](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html),
[`KMeans`](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html),
[`GaussianMixture`](https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html),
[`IsolationForest`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html),
[`silhouette_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html),
and [`adjusted_rand_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html).

## Visualization and application

| Library | Project use | Official reference |
| --- | --- | --- |
| Matplotlib ≥ 3.11.2 | static analytical figures exported by the notebooks | [Matplotlib documentation](https://matplotlib.org/stable/) |
| seaborn ≥ 0.13.2 | statistical distributions, relationships, and heatmaps | [seaborn documentation](https://seaborn.pydata.org/) |
| Plotly ≥ 7.1.0 | interactive charts in the result application | [Plotly Python documentation](https://plotly.com/python/) |
| Streamlit ≥ 1.67.0 | read-only result interface and future inference upload | [Streamlit documentation](https://docs.streamlit.io/) |

`requests` and `rich` are declared runtime dependencies, but no direct import was found
in the current source or notebooks. Their continued inclusion should be reviewed before
the final release: [Requests documentation](https://requests.readthedocs.io/en/latest/)
and [Rich documentation](https://rich.readthedocs.io/en/stable/).

## Documentation and quality

| Tool | Project use | Official reference |
| --- | --- | --- |
| MkDocs | static documentation build | [MkDocs documentation](https://www.mkdocs.org/) |
| Material for MkDocs | documentation theme and language selector | [Material documentation](https://squidfunk.github.io/mkdocs-material/) |
| mkdocs-static-i18n | English/Portuguese builds and localized navigation | [plugin documentation](https://ultrabug.github.io/mkdocs-static-i18n/) |
| pytest | automated tests | [pytest documentation](https://docs.pytest.org/) |
| Ruff | linting and import/style checks | [Ruff documentation](https://docs.astral.sh/ruff/) |
| mypy | static type checking | [mypy documentation](https://mypy.readthedocs.io/) |
| uv | dependency locking and reproducible commands | [uv documentation](https://docs.astral.sh/uv/) |

## Data source

The analytical source is
[Steel Industry Energy Consumption](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption),
published by the UCI Machine Learning Repository:

> Sathishkumar V E, Changsun Shin, and Yongyun Cho (2021), *Steel Industry Energy
> Consumption*, UCI Machine Learning Repository, DOI
> [10.24432/C52G8C](https://doi.org/10.24432/C52G8C), CC BY 4.0.

## Reproducibility boundary

Official documentation explains library behavior; the project's numerical impressions
come from the stored notebook executions. See [Initial Findings](initial-findings.md) for
the notebook-derived evidence and its interpretation limits.
