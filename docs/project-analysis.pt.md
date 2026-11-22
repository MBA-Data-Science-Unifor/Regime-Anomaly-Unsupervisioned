# Estrutura do Projeto

## Fluxo de trabalho

    artifacts/data/raw/Steel_industry_data.csv
            ↓
    01_EDA.ipynb
            ↓
    02_preprocessing.ipynb
            ↓
    03_Modeling.ipynb
            ↓
    artifacts/{data/processed,tables,images,models,metadata}
            ↓
    MkDocs e Streamlit

## Contrato de publicação

| Caminho | Conteúdo | Política no Git |
| --- | --- | --- |
| artifacts/data/raw | fonte local da UCI | ignorado |
| artifacts/data/processed | dicionários e dados preparados | ignorado |
| artifacts/tables | tabelas analíticas geradas | ignorado |
| artifacts/images | figuras geradas | ignorado |
| artifacts/models | futuros pacotes serializados | ignorado |
| artifacts/metadata | futuras métricas e manifesto | ignorado |
| artifacts/notebooks | investigação reproduzível | versionado sem saídas |

A lógica reutilizável aprovada deve sair dos notebooks e ir para `src/regime_anomaly`.
A documentação registra a metodologia estável e evidências preliminares, enquanto as
saídas pesadas são regeneradas localmente.
