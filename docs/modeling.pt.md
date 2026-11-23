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
