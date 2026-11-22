# Preparação dos Dados

A preparação está implementada experimentalmente em
`artifacts/notebooks/02_preprocessing.ipynb`. As operações reutilizáveis são expostas por
`src/regime_anomaly/preprocessing.py`; a seleção final de variáveis ainda está em revisão.

## Pipeline implementado

1. interpretar a data com semântica de dia-primeiro;
2. preservar uma cópia bruta imutável;
3. separar data, `Load_Type`, variáveis numéricas e categorias de calendário;
4. derivar variáveis temporais aprovadas sem vazar informações futuras;
5. padronizar as variáveis numéricas;
6. aplicar one-hot encoding a `WeekStatus` e `Day_of_week`;
7. ajustar cada transformação apenas no período de treinamento apropriado;
8. serializar o pré-processamento com o modelo selecionado.

A comparação de escores usada nesta seleção experimental está publicada em
[Descobertas iniciais](initial-findings.md) e pode ser regenerada a partir da saída
armazenada do notebook com `python scripts/generate_docs_figures.py`.

## Limite contra vazamento

`Load_Type` não é uma variável de treinamento. Sua cardinalidade define a atual hipótese
de três regimes, enquanto seus valores ficam reservados para avaliação externa posterior.
Divisões sensíveis ao tempo são preferidas às divisões somente aleatórias porque
observações adjacentes de 15 minutos não são independentes.

## Decisões ainda em aberto

- tratamento de variáveis assimétricas e valores extremos;
- manutenção de `NSM` como numérica ou conversão em variáveis cíclicas seno/cosseno;
- tratamento de redundância entre variáveis elétricas fortemente associadas;
- conjuntos de variáveis para as tarefas de regimes e anomalias;
- estratégia de calibração dos limiares de anomalia.
