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

- EDA (`01_EDA.ipynb`), pré-processamento (`02_preprocessing.ipynb`) e modelagem
  (`03_Modeling.ipynb`) implementados e executáveis em sequência;
- modelo selecionado por protocolo fixado antes dos resultados: **K-Means com três
  regimes** usando só variáveis elétricas — ocioso indutivo, ocioso capacitivo e produção;
- **Isolation Forest** com limiar de 1% calibrado na validação; na v1.1, alertas em trocas de regime são suprimidos (49 → 5 alertas no teste);
- avaliação final congelada em nov–dez; concordância com `Load_Type` é moderada
  (ARI 0,34) porque `Load_Type` segue uma tabela tarifária por horário, não o estado
  elétrico;
- modelo, métricas, resultados e manifesto de integridade publicados em `artifacts/`;
- decisões, nomes dos regimes e triagem dos alertas aguardam revisão da equipe; o material está em `04_Review.ipynb` e na página Team Review da documentação.

## Equipe

- Alexandre Franco
- Caio Cunha Franco
- Rodrigo Franco

## Notebooks

1. `01_EDA.ipynb`: qualidade, distribuições, relações, PCA, t-SNE e baselines não supervisionados;
2. `02_preprocessing.ipynb`: correção de timestamps, partição temporal, conjuntos de features e transformações;
3. `03_Modeling.ipynb`: protocolo, comparação de candidatos, anomalias, congelamento, avaliação no teste e publicação.
4. `04_Review.ipynb`: material para revisão da equipe — registro de decisões, evidências dos regimes e planilha de triagem dos alertas;
5. `05_Transition_Filter.ipynb`: filtro de alertas em trocas de regime (modelo v1.1).

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

Antes de executar, baixe `Steel_industry_data.csv` da
[UCI](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption) para
`artifacts/data/raw/`. O projeto nunca baixa o arquivo automaticamente.

```bash
uv sync --locked --group analysis --group docs --group test
uv run invoke notebooks          # executa 01 a 05 em ordem e regenera os artefatos
uv run regime-analysis           # confere os artefatos contra o manifesto (SHA-256)
uv run streamlit run src/app.py
uv run invoke docs --build --strict
uv run pytest
```

Para retomar a partir de um notebook: `uv run invoke notebooks --start 03_Modeling`.
O `requirements.txt` é exportado do `uv.lock` (`uv export`) para quem usa `pip`.

A aplicação Streamlit deve apenas consumir artefatos aprovados; treinamento não faz
parte do processo web.

## Documentação

A documentação MkDocs descreve o problema, a origem dos dados, a metodologia,
as impressões iniciais, as decisões adiadas e os critérios de avaliação.

