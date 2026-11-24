# Modelagem

A modelagem final pertence a `artifacts/notebooks/03_Modeling.ipynb`. Os algoritmos
mostrados na EDA são baselines, não um modelo de produção selecionado.

## Hipótese atual

Os modelos principais de regime usam exatamente três grupos, derivados da quantidade de
categorias de `Load_Type` sem usar suas identidades durante o ajuste.

## Baselines mantidos

- K-Means para perfis de centroides escaláveis e interpretáveis;
- GMM de três componentes com covariância diagonal para sobreposição probabilística;
- Isolation Forest para pontuação global de anomalias.

## Próxima comparação de anomalias

O Isolation Forest atual é um baseline global com contaminação exploratória de 2%. O
rastreamento pós-hoc por `Load_Type` revelou concentração desigual de sinais, o que não
é uma métrica de erro porque carga não é rótulo de falha. A próxima comparação deve testar
uma versão contextual: perfis descobertos sem supervisão, hora e tipo de dia definem o
contexto; os desvios de consumo e das variáveis elétricas dentro desse contexto recebem o
score de anomalia. Limiares e persistência de alertas devem ser congelados fora dos mesmos
dados usados para relato.

Uma futura classificação supervisionada de `Load_Type` terá objetivo próprio: prever o
regime conhecido e ser avaliada com divisão temporal, macro-F1 e acurácia balanceada. Ela
não transforma `Load_Type` em rótulo de falha e não valida o detector de anomalias.

## Candidatos adiados

DBSCAN/HDBSCAN, agrupamento hierárquico, K-Medoids, agrupamento espectral, SOM, UMAP,
autoencoders, LOF, One-Class SVM e métodos de covariância robusta permanecem como
alternativas documentadas. Eles devem ser introduzidos apenas quando suas premissas
responderem a uma falha específica dos baselines.

## Registro obrigatório dos experimentos

Cada experimento deve registrar hash dos dados, divisão temporal, conjunto de variáveis,
pré-processamento ajustado, algoritmo, parâmetros, semente, tempo de execução, métricas
internas, estabilidade, tamanhos dos grupos, desvio temporal e limitações. O modelo final
deve ser serializado junto com o pré-processamento em `artifacts/models` e acompanhado de
metadados.
