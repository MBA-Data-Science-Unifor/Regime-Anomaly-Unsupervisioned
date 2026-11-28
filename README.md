# Steel Industry Energy Consumption — Regimes e Anomalias

Projeto de análise não supervisionada do consumo energético de uma indústria siderúrgica
sul-coreana. O objetivo é investigar três regimes operacionais, definidos pela cardinalidade
de `Load_Type`, e sinalizar observações incomuns sem usar os rótulos para treinar os modelos.

## Base de dados

A fonte é o conjunto
[Steel Industry Energy Consumption](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption),
publicado no UCI Machine Learning Repository. Uma cópia do CSV bruto é versionada no
repositório, para que os notebooks possam ser executados logo após o clone:

```text
artifacts/data/raw/Steel_industry_data.csv
```

A base contém 35.040 medições de 2018 em intervalos de 15 minutos, 11 colunas e
três níveis de carga: `Light_Load`, `Medium_Load` e `Maximum_Load`.

## Estado atual

- EDA (`01_EDA.ipynb`), pré-processamento (`02_Preprocessing.ipynb`) e modelagem (`03_Modeling.ipynb`) implementados e
  executáveis em sequência;
- modelo selecionado por protocolo fixado antes dos resultados: **K-Means com três
  regimes** usando só variáveis elétricas — ocioso indutivo, ocioso capacitivo e produção;
- **Isolation Forest** com limiar de 1% calibrado na validação; na v1.1, alertas em trocas de regime são suprimidos (49 → 5 alertas no teste);
- avaliação em nov–dez após a seleção do modelo; a EDA anterior incluiu todo o ano,
  portanto o teste não constitui uma avaliação plenamente independente. A concordância com `Load_Type` é moderada
  (ARI 0,34) porque `Load_Type` segue uma tabela tarifária por horário, não o estado
  elétrico;
- modelo, métricas, resultados e manifesto de integridade publicados em `artifacts/`;
- decisões, nomes dos regimes e triagem dos alertas aguardam revisão da equipe; o material está em `04_Review.ipynb` e na página Team Review da documentação.
- experimento supervisionado separado de KNN para `Load_Type`: F1 macro de 0,919 na
  validação e 0,593 no teste histórico, com calendário; os resultados exigem investigação
  da diferença entre períodos;
- dashboard Streamlit de monitoramento (visão geral, monitoramento, alertas, modelos e
  relatórios) lendo os resultados publicados, com teste por CSV e cenários sintéticos
  para investigar a sensibilidade dos alertas;

O dashboard organiza visão geral, monitoramento, alertas, modelos, cenários e artefatos
em abas. A aba de artefatos mostra origem e verificação de integridade; a aba de cenários
permite testar alterações sintéticas em uma leitura de validação e comparar o alerta
bruto com o filtrado. Essas simulações não são falhas confirmadas.

## Equipe

- Alexandre Franco — Analista de dados e modelagem
- Caio Cunha Franco — Engenheiro de IA
- Rodrigo Franco — Engenheiro de dados

## Notebooks

1. `01_EDA.ipynb`: qualidade, distribuições, relações, PCA, t-SNE e baselines não supervisionados;
2. `02_Preprocessing.ipynb`: síntese da comparação exploratória e protocolo publicado — correção de timestamps, partição treino / validação / teste, conjuntos de features e transformações;
3. `03_Modeling.ipynb`: seleciona os regimes, calibra o detector de anomalias, publica a versão v1.1 e avalia um KNN supervisionado para `Load_Type`;
4. `04_Review.ipynb`: revisão da equipe e experimentos de sensibilidade para os modelos supervisionado e não supervisionados, sem republicação automática.

O notebook 03 compara também a concordância dos agrupamentos com `Load_Type` após o
ajuste, sem utilizar o rótulo para treinar os modelos não supervisionados.

## Artefatos e versionamento

### Snapshot de producao

Em adicao ao CSV bruto, o Git deve conter somente o conjunto aprovado e lido na
execucao: `analysis_results.csv`, `prepared_dataset.csv`, `preprocessing.json`,
`final_metrics.json`, `manifest.json` e `final_model.joblib`. O modelo tambem e usado
por `test_published_model_scores_raw_uci_rows`. Tabelas, imagens, modelos auxiliares e
saidas intermediarias continuam regeneraveis e ignorados.

O CSV bruto `artifacts/data/raw/Steel_industry_data.csv` é versionado para garantir uma
execução reproduzível dos notebooks. As demais saídas regeneráveis não são versionadas
para evitar crescimento do repositório. O `.gitignore` preserva apenas os arquivos
`.gitkeep` dentro de `artifacts/data/processed`, `images`, `tables`, `models` e
`metadata`.

Ao executar o EDA, são produzidos localmente:

- `artifacts/data/processed/dicionario_dados.csv`;
- tabelas exploratórias em `artifacts/tables/`;
- gráficos PNG em `artifacts/images/`.

O dashboard de monitoramento consome o que o notebook 03 publica e o notebook 04 revisa:

- `artifacts/data/processed/analysis_results.csv`, com a série temporal enriquecida
  (medições, `regime_name`, `anomaly_score`, `is_anomaly_raw`, `regime_boundary` e
  `is_anomaly`);
- `artifacts/metadata/final_metrics.json`, com métricas congeladas;
- o modelo serializado em `artifacts/models/final_model.joblib`.

Os nomes de coluna publicados são convertidos para os nomes canônicos do dashboard em
`src/regime_anomaly/dashboard.py` (`COLUMN_ALIASES`). Estado e motivo do alerta
(`alert_severity`, `alert_reason`) ainda não são publicados; até lá, o dashboard marca
como "Atenção" as leituras com `is_anomaly`.

## Ambiente e execução

Requer Python 3.12 ou superior e [uv](https://docs.astral.sh/uv/).

O CSV bruto já está disponível em `artifacts/data/raw/Steel_industry_data.csv`. Caso
precise restaurá-lo, baixe `Steel_industry_data.csv` da
[UCI](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption) e
mantenha esse mesmo nome e caminho. O projeto nunca baixa o arquivo automaticamente.

```bash
uv sync --locked --group analysis --group docs --group test
uv run invoke notebooks          # executa 01 a 04 em ordem e regenera os artefatos
uv run regime-analysis           # confere os artefatos contra o manifesto (SHA-256)
uv run streamlit run src/app.py
uv run invoke docs --build --strict
uv run pytest
```

Para retomar a partir de um notebook: `uv run invoke notebooks --start 03_Modeling`.
O `requirements.txt` é exportado do `uv.lock` (`uv export`) para quem usa `pip`.

A aplicação Streamlit apenas consome artefatos aprovados; treinamento não faz parte
do processo web. Ela reproduz resultados históricos publicados como uma simulação de
monitoramento e verifica alterações nos artefatos a cada 30 segundos enquanto a página
está aberta. O botão de atualização manual continua disponível. A configuração nativa
fica em `.streamlit/config.toml` e ativa a atualização ao salvar código em desenvolvimento.
Essas atualizações não executam os notebooks nem buscam dados novos. Alertas
indicam comportamento atípico para investigação operacional: não são diagnósticos de
falha, previsões de manutenção ou ordens de serviço.

A classificação supervisionada de `Load_Type` é uma comparação separada e não substitui
a segmentação e a detecção de anomalias não supervisionadas. Ela usa medições do mesmo
intervalo e classifica após a leitura, sem prever antecipadamente o consumo.

## Documentação

A documentação MkDocs descreve o problema, a origem dos dados, a metodologia,
as impressões iniciais, as decisões adiadas e os critérios de avaliação.
