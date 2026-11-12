# Steel Industry Energy Consumption — Regimes e Anomalias

Projeto de análise não supervisionada do consumo energético de uma indústria siderúrgica
sul-coreana. O objetivo é investigar três regimes operacionais, definidos pela cardinalidade
de `Load_Type`, e sinalizar observações incomuns sem usar os rótulos para treinar os modelos.

## Base de dados

A fonte é o conjunto
[Steel Industry Energy Consumption](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption),
publicado no UCI Machine Learning Repository. O arquivo local esperado é:

```text
artifacts/data/raw/Steel_industry_data.csv
```

A base contém 35.040 medições de 2018 em intervalos de 15 minutos, 11 colunas e
três níveis de carga: `Light_Load`, `Medium_Load` e `Maximum_Load`.

## Estado atual

- o EDA foi estruturado e documentado em `artifacts/notebooks/01_EDA.ipynb`;
- o dicionário de dados, tabelas e imagens são gerados localmente em `artifacts/`;
- K-Means e GMM são explorados com três grupos, sem usar os valores de `Load_Type`;
- Isolation Forest é usado apenas como diagnóstico exploratório de anomalias;
- preparação, comparação final, avaliação congelada e modelo de produção ainda estão pendentes.

Resultados atuais são impressões exploratórias, não conclusões finais.

## Equipe

- Alexandre Franco
- Caio Cunha Franco
- Rodrigo Franco

## Notebooks

1. `01_EDA.ipynb`: qualidade, distribuições, relações, PCA, t-SNE e baselines não supervisionados;
2. `02_preprocessing.ipynb`: preparação reproduzível, ainda em desenvolvimento;
3. `03_Modeling.ipynb`: comparação e seleção final, ainda em desenvolvimento.

## Artefatos e versionamento

Dados locais e saídas regeneráveis não são versionados para evitar crescimento do
repositório. O `.gitignore` preserva apenas os arquivos `.gitkeep` dentro de
`artifacts/data`, `images`, `tables`, `models` e `metadata`.

Ao executar o EDA, são produzidos localmente:

- `artifacts/data/processed/dicionario_dados.csv`;
- tabelas exploratórias em `artifacts/tables/`;
- gráficos PNG em `artifacts/images/`.

## Ambiente e execução

Requer Python 3.12 ou superior e [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked
uv run streamlit run src/app.py
uv run --group docs invoke docs --build --strict
uv run --group test pytest
```

A aplicação Streamlit deve apenas consumir artefatos aprovados; treinamento não faz
parte do processo web.

## Documentação

A documentação MkDocs descreve o problema, a origem dos dados, a metodologia,
as impressões iniciais, as decisões adiadas e os critérios de avaliação.

