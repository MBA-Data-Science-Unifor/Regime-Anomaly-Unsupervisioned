# Avaliação

A avaliação não é realizada na EDA. Ela deve usar um protocolo congelado e distinguir
geometria dos regimes, estabilidade, ordenação de anomalias e concordância externa
opcional.

## Evidências internas de agrupamento

- silhueta;
- Davies–Bouldin;
- Calinski–Harabasz;
- equilíbrio entre tamanhos dos grupos;
- estabilidade entre reamostragens e sementes;
- estabilidade temporal e desvio dos centroides.

## Evidências probabilísticas e de anomalias

- verossimilhança do GMM, diagnósticos AIC/BIC e incerteza da atribuição;
- distribuição dos escores do Isolation Forest e sensibilidade à contaminação;
- estabilidade do conjunto de anomalias mais bem classificadas;
- revisão por janela temporal e contexto operacional.

## Avaliação externa, somente depois

Após o congelamento das escolhas de modelo, `Load_Type` pode apoiar medidas de
concordância como ARI, NMI, tabelas de contingência e interpretação dos regimes. Elas não
são métricas de treinamento supervisionado e não devem influenciar o ajuste não
supervisionado.

Se uma tarefa supervisionada for aprovada futuramente, ela exigirá objetivo, divisão,
baseline e métricas próprios. Acurácia isolada é insuficiente para categorias
desbalanceadas.

## Salvaguardas

Gráficos de PCA/t-SNE nunca substituem métricas no espaço transformado original. Os
limiares não podem ser selecionados nos mesmos dados usados no relatório final. Os
valores atuais da EDA são preliminares.
