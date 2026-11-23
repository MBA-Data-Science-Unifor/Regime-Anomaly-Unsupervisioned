# Referências Técnicas

Esta página registra as referências oficiais das bibliotecas e ferramentas declaradas
pelo projeto. As versões mínimas vêm de `pyproject.toml`; o ambiente resolvido está
registrado em `uv.lock`.

## Dados e computação científica

| Biblioteca | Uso no projeto | Referência oficial |
| --- | --- | --- |
| Python ≥ 3.12 | linguagem e biblioteca-padrão | [documentação do Python](https://docs.python.org/3/) |
| NumPy ≥ 2.5.4 | arrays, variáveis cíclicas, verificações numéricas e artefatos dos notebooks | [documentação do NumPy](https://numpy.org/doc/stable/) |
| pandas ≥ 3.1.1 | leitura de CSV, transformações tabulares, séries temporais e resumos | [documentação do pandas](https://pandas.pydata.org/docs/) |
| scikit-learn ≥ 1.9.1 | pré-processamento, PCA, K-Means, GMM, Isolation Forest e métricas | [documentação do scikit-learn](https://scikit-learn.org/stable/) |
| joblib ≥ 1.6.0 | serialização do pré-processamento e dos modelos | [documentação do joblib](https://joblib.readthedocs.io/en/stable/) |

As principais APIs do scikit-learn usadas nos notebooks são
[`ColumnTransformer`](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html),
[`StandardScaler`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html),
[`OneHotEncoder`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html),
[`PCA`](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html),
[`KMeans`](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html),
[`GaussianMixture`](https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html),
[`IsolationForest`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html),
[`silhouette_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
e [`adjusted_rand_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html).

## Visualização e aplicação

| Biblioteca | Uso no projeto | Referência oficial |
| --- | --- | --- |
| Matplotlib ≥ 3.11.2 | figuras analíticas estáticas exportadas pelos notebooks | [documentação do Matplotlib](https://matplotlib.org/stable/) |
| seaborn ≥ 0.13.2 | distribuições estatísticas, relações e mapas de calor | [documentação do seaborn](https://seaborn.pydata.org/) |
| Plotly ≥ 7.1.0 | gráficos interativos na aplicação de resultados | [documentação Python do Plotly](https://plotly.com/python/) |
| Streamlit ≥ 1.67.0 | interface somente leitura e futuro upload para inferência | [documentação do Streamlit](https://docs.streamlit.io/) |

`requests` e `rich` estão declarados como dependências de execução, mas nenhum import
direto foi encontrado no código ou nos notebooks atuais. A permanência dessas
dependências deve ser revisada antes da versão final: [documentação do
Requests](https://requests.readthedocs.io/en/latest/) e [documentação do
Rich](https://rich.readthedocs.io/en/stable/).

## Documentação e qualidade

| Ferramenta | Uso no projeto | Referência oficial |
| --- | --- | --- |
| MkDocs | construção da documentação estática | [documentação do MkDocs](https://www.mkdocs.org/) |
| Material for MkDocs | tema e seletor de idioma | [documentação do Material](https://squidfunk.github.io/mkdocs-material/) |
| mkdocs-static-i18n | builds em inglês/português e navegação localizada | [documentação do plugin](https://ultrabug.github.io/mkdocs-static-i18n/) |
| pytest | testes automatizados | [documentação do pytest](https://docs.pytest.org/) |
| Ruff | lint e verificações de imports/estilo | [documentação do Ruff](https://docs.astral.sh/ruff/) |
| mypy | verificação estática de tipos | [documentação do mypy](https://mypy.readthedocs.io/) |
| uv | lock de dependências e comandos reproduzíveis | [documentação do uv](https://docs.astral.sh/uv/) |

## Fonte dos dados

A fonte analítica é
[Steel Industry Energy Consumption](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption),
publicada pelo UCI Machine Learning Repository:

> Sathishkumar V E, Changsun Shin e Yongyun Cho (2021), *Steel Industry Energy
> Consumption*, UCI Machine Learning Repository, DOI
> [10.24432/C52G8C](https://doi.org/10.24432/C52G8C), CC BY 4.0.

## Limite de reprodutibilidade

A documentação oficial explica o comportamento das bibliotecas; as impressões numéricas
do projeto vêm das execuções armazenadas nos notebooks. Consulte
[Descobertas iniciais](initial-findings.md) para as evidências derivadas dos notebooks e
seus limites de interpretação.
