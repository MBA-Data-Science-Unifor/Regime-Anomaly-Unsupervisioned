# Modelagem

A modelagem está implementada em `artifacts/notebooks/03_Modeling.ipynb`; o código que
precisa coincidir entre o notebook e a inferência fica em
`src/regime_anomaly/modeling.py`.

## Protocolo (fixado antes dos resultados)

- **Dados:** treino de janeiro a agosto, validação de setembro a outubro, teste de
  novembro a dezembro. Todo ajuste usa apenas o treino.
- **Candidatos de regime (três grupos):** K-Means (`n_init=20`), GMM com covariância
  diagonal e GMM com covariância completa (`n_init=5`), cada um no conjunto de variáveis
  `regime` (principal) e em `regime_with_calendar` (sensibilidade).
- **Evidências na validação:** silhueta, Davies–Bouldin, Calinski–Harabasz, participação
  do menor grupo, estabilidade entre sementes (5 sementes), estabilidade em 10
  reamostragens bootstrap por dia e estabilidade temporal (concordância com um modelo
  reajustado na validação).
- **Regra de seleção:** entre os candidatos `regime`, são elegíveis os que tiverem ARI
  médio de bootstrap ≥ 0,80 e menor grupo ≥ 5%; vence a maior silhueta na validação.
- **Anomalias:** Isolation Forest no conjunto de variáveis `anomaly`. Premissa
  operacional: 1% das leituras sinalizadas; o limiar é o percentil 99 dos escores da
  validação e não é reajustado no teste.

## Comparação na validação

| Conjunto de variáveis | Candidato | Silhueta | ARI de bootstrap | ARI temporal |
| --- | --- | --- | --- | --- |
| regime | **kmeans** | **0,823** | **0,999** | **0,999** |
| regime | gmm_diag | 0,758 | 1,000 | 0,841 |
| regime | gmm_full | 0,758 | 1,000 | 0,836 |
| regime_with_calendar | kmeans | 0,384 | 0,998 | 0,995 |
| regime_with_calendar | gmm_diag | 0,347 | 0,664 | 0,875 |
| regime_with_calendar | gmm_full | 0,288 | 0,496 | 0,416 |

Adicionar entradas de calendário torna os GMMs instáveis (ARI bootstrap de 0,66 e 0,50).
A silhueta também cai pela metade, mas os dois conjuntos têm 5 e 10 dimensões, então
essas silhuetas não são estritamente comparáveis; a decisão se apoia na estabilidade.
Selecionar pela silhueta também tende a favorecer o K-Means em relação ao GMM.

## Regimes selecionados

Os regimes são nomeados pela assinatura elétrica (`order_by_profile`), não pela ordem de
consumo, porque os dois regimes ociosos têm quase o mesmo consumo.

| Regime | Consumo mediano | Assinatura | Quando |
| --- | --- | --- | --- |
| ocioso indutivo | ~3,2 kWh | energia reativa atrasada, FP atrasado ~60% | noite |
| ocioso capacitivo | ~3,9 kWh | energia reativa **adiantada**, FP adiantado ~22% | pausas dentro do horário de trabalho |
| produção | ~61 kWh | FP atrasado ~92% | horário de trabalho |

O regime capacitivo sugere que a compensação de potência reativa permanece ligada quando
a carga cai durante o dia.

## Pacote serializado

`artifacts/models/final_model.joblib` armazena um `ModelBundle` com os dois
pré-processadores ajustados, o modelo de regimes, o mapa de nomes dos regimes, o
Isolation Forest, o limiar da validação, o indicador `transition_filter` (ligado desde a
v1.1; consulte [Avaliação](evaluation.md#filtro-de-transicao-modelo-v11)) e metadados
(hash dos dados, versões, motivo da seleção).
`ModelBundle.predict` aceita um frame em snake_case no layout da UCI e ignora
`Load_Type` se estiver presente. Ele retorna `is_anomaly_raw` (escore acima do limiar),
`regime_boundary` (calculado em ordem cronológica a partir de `timestamp` ou `date`,
nunca através de lacunas) e `is_anomaly` (indicador bruto, menos as fronteiras quando o
filtro está ligado).

## Candidatos adiados

DBSCAN/HDBSCAN, agrupamento hierárquico, K-Medoids, agrupamento espectral, SOM, UMAP,
autoencoders, LOF, One-Class SVM e covariância robusta permanecem como alternativas
documentadas. O baseline selecionado atendeu a todos os critérios do protocolo, então
nenhum deles foi necessário para responder a uma falha específica.
