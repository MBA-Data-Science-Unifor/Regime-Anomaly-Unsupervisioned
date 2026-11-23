# Análise Exploratória

A EDA implementada está registrada em `artifacts/notebooks/01_EDA.ipynb`.

## Estrutura

1. contrato dos dados, qualidade e dicionário gerado;
2. análise univariada numérica, categórica e temporal;
3. relações entre variáveis com `Load_Type` excluído;
4. projeções PCA e t-SNE;
5. diagnósticos de assimetria, IQR, Spearman e dia-hora;
6. baselines de K-Means e GMM com três regimes;
7. sinais exploratórios do Isolation Forest;
8. justificativas para técnicas selecionadas e adiadas.

## Regras de interpretação

- `Load_Type` fornece apenas o número três e sua frequência descritiva;
- projeções não definem grupos;
- cotovelo, silhueta, AIC e BIC são diagnósticos, não seletores automáticos;
- extremos segundo o IQR não são equivalentes a anomalias;
- sinais do Isolation Forest não são incidentes confirmados;
- nenhum estimador supervisionado ou métrica baseada em rótulo pertence à EDA.

## Saídas geradas

O notebook grava um dicionário de dados, resumos CSV e 20 figuras PNG em `artifacts`.
Essas saídas são deliberadamente ignoradas pelo Git e devem ser regeneradas localmente.
As impressões quantitativas estáveis estão resumidas em
[Descobertas iniciais](initial-findings.md).

A documentação publica versões compactas e reproduzíveis das figuras de correlação,
consumo mês–hora e diagnóstico do K-Means. Elas podem ser regeneradas com:

    python scripts/generate_docs_figures.py

Cada figura é acompanhada de um limite de interpretação em
[Descobertas iniciais](initial-findings.md); as imagens são evidências, não provas
isoladas de causalidade ou validade de negócio.
