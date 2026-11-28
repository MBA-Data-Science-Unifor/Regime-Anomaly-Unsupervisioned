# Avaliação

A avaliação da versão base usa novembro–dezembro após a fixação do modelo,
pré-processamento e limiar. Como a EDA anterior examinou todo o ano e a revisão
retrospectiva também consultou o teste, os resultados não representam uma avaliação
plenamente independente. Os valores vêm de `artifacts/metadata/final_metrics.json`.

## Evidências internas no teste

| Métrica | Validação | Teste |
| --- | --- | --- |
| Silhueta | 0,823 | 0,768 |
| Davies–Bouldin | 0,261 | 0,332 |
| Participação do menor grupo | 21,3% | 24,3% |
| Taxa de alertas (meta de 1%) | 1,00% | 0,84% |

As participações dos regimes permanecem próximas entre os períodos: ocioso indutivo
38% / 42% / 41%, ocioso capacitivo 24% / 21% / 24%, produção 38% / 37% / 34%
(treino / validação / teste).

O notebook 03 complementa as métricas globais com a silhueta média e mediana por
regime e a proporção de observações com silhueta negativa, em amostras reprodutíveis
da validação e do teste. Valores negativos indicam possível sobreposição com outro
grupo; não são prova de erro. Davies–Bouldin menor e Calinski–Harabasz maior são
indicadores internos adicionais, interpretados no mesmo espaço de features. A
estabilidade entre sementes, bootstrap por dia e janelas temporais complementa a
geometria. Esses indicadores não demonstram que os grupos correspondem a estados
operacionais reais.

| Regime | Silhueta média na validação | Silhueta média no teste |
| --- | ---: | ---: |
| Ocioso indutivo | 0,921 | 0,813 |
| Ocioso capacitivo | 0,889 | 0,843 |
| Produção | 0,670 | 0,662 |

São amostras de 5.000 leituras por partição, e a proporção de silhuetas negativas
ficou abaixo de 0,2% em cada regime. Produção é o grupo menos compacto e separado
segundo esse diagnóstico. Fonte: `modelagem_diagnostico_interno_regimes.csv`.

## Evidências de anomalias

O notebook 04 e a página **Cenários** do dashboard permitem executar testes de
sensibilidade: uma leitura histórica de validação é comparada a alterações sintéticas
de consumo, reativa e fator de potência, mantendo as leituras vizinhas. O resultado
mostra escore, alerta bruto, fronteira e alerta após o filtro. Os cenários podem não
ser fisicamente plausíveis e não possuem rótulos de falha; são testes de comportamento,
não medidas de precisão ou de sensibilidade do detector. A validação operacional deve
incluir leituras com e sem alerta e, idealmente, dados posteriores independentes.

Em uma execução com o modelo publicado e a leitura de referência de 01/09/2018 às
20:45, o limiar era 0,6247. Consumo elevado, reativa elevada, fator de potência baixo
e uma combinação moderada produziram escores entre 0,5326 e 0,6197, sem alerta; um
estresse combinado mais intenso atingiu 0,6806 e gerou alerta. Isso mostra a resposta
do modelo a essas intervenções naquela leitura, e não garante que os cenários sejam
falhas nem que o comportamento se repita em outras condições.

- o limiar do Isolation Forest é 0,6247: percentil 99 dos escores da validação;
- o top 1% da validação se sobrepõe em 87%, em média, entre cinco sementes (Jaccard),
  sustentando a reprodutibilidade dos sinais mais bem classificados;
- cerca de 40% dos alertas da validação se repetem no mesmo dia da semana e horário em
  três ou mais semanas; recorrência é contexto operacional, não prova de falha;
- a taxa de 1% é uma premissa operacional: não há rótulos de falha para estimá-la.

O notebook também compara mediana, percentis 95 e 99 dos escores e taxa bruta de
alertas entre partições. Mudanças sugerem deriva, mas diferenças podem refletir
sazonalidade e não medem precisão. Os escores de treino são apresentados como
referência descritiva, pois o detector foi ajustado nesses mesmos dados.

Os percentis 99 foram 0,635 no treino, 0,625 na validação e 0,620 no teste; as
taxas brutas foram 2,02%, 1,01% e 0,84%, respectivamente. Fonte:
`modelagem_diagnostico_escores_anomalia.csv`.

## Concordância externa com `Load_Type`

### Experimento supervisionado separado

O notebook `03_Modeling.ipynb` compara KNN com variáveis elétricas e com calendário,
selecionando conjunto e número de vizinhos pelo F1 macro na validação. O melhor
candidato foi KNN com calendário e 15 vizinhos: F1 macro **0,919** na validação e
**0,593** no teste histórico. No teste, a acurácia foi **69,9%**, contra **53,1%**
para a classe majoritária do treino; as sensibilidades foram 93,6% para `Light_Load`,
36,4% para `Maximum_Load` e 47,9% para `Medium_Load`. A queda entre períodos merece
investigação, sem atribuir uma causa apenas a partir desses resultados.

O experimento classifica medições já disponíveis, usa os rótulos no ajuste e não
valida o detector de anomalias. Os dados do teste já foram consultados em análises
anteriores; um período posterior independente é necessário para avaliar generalização.

No notebook 04, uma comparação adicional selecionou Extra Trees com calendário na
validação (F1 macro 0,954), frente a 0,919 do KNN. No teste histórico, ambos tiveram
F1 macro aproximadamente 0,593; portanto, o aumento na validação não confirmou melhora
nesse período. Para regimes, retirar o fator de potência adiantado resultou em silhueta
0,827 contra 0,821 na amostra de validação, em espaços diferentes; o resultado não é
evidência suficiente para substituir o modelo. Na comparação exploratória do Isolation
Forest com 150 árvores, o Jaccard médio entre sementes foi 0,762 para `max_samples=256`
e 0,675 para 1.024. Estabilidade não equivale à detecção correta de falhas.

### Comparação não supervisionada com os rótulos

Além do modelo selecionado, o notebook 03 compara K-Means e os GMMs, com e sem
calendário, por ARI e NMI na validação e no teste. A acurácia, a acurácia balanceada e
o F1 macro usam uma associação de cada cluster à classe mais frequente no treino;
mais de um cluster pode receber a mesma classe. Essa comparação é posterior ao ajuste
e não seleciona nem retreina os modelos. A inclusão do calendário muda o espaço dos
agrupamentos e pode facilitar a concordância com o rótulo sem melhorar a identificação
de regimes elétricos. O teste continua retrospectivo e não independente.

Na execução comparativa, o K-Means elétrico teve ARI **0,342** e F1 macro **0,540**
no teste; o K-Means com calendário obteve **0,355** e **0,546**. Os GMMs elétricos
obtiveram ARI de **0,157–0,167** e F1 macro de **0,441–0,444**. A proximidade dos
resultados de K-Means com e sem calendário não comprova uma melhora generalizável,
e a concordância com `Load_Type` não valida falhas ou estados operacionais.

O notebook 03 também apresenta acurácia, acurácia balanceada, precisão, sensibilidade,
F1, matriz de confusão e curvas ROC um contra os demais. Cada cluster recebe a classe
mais frequente no treino; as proporções de classes no treino fornecem os escores para a
ROC. Assim, essas métricas medem concordância com `Load_Type`, não qualidade de detecção
de falhas. Os escores são constantes dentro de cada cluster e não são probabilidades
calibradas para o teste. Uma classe pode não ser atribuída a nenhum cluster; nesse caso,
seu F1 e sensibilidade revelam essa limitação. A comparação inclui a classe majoritária
do treino como referência. Como não há rótulos de falha, ROC, acurácia, precisão e
sensibilidade de anomalias não podem ser calculadas de forma válida nesta base.

No teste, a acurácia do mapeamento aprendido no treino foi **59,6%**, frente a
**53,1%** para a classe majoritária do treino. A acurácia balanceada foi **55,9%**
e o F1 macro **54,0%**. A sensibilidade foi 71,6% para `Light_Load`, 62,8% para
`Maximum_Load` e 33,4% para `Medium_Load`. As AUCs foram, respectivamente, 0,881,
0,708 e 0,749; são calculadas sobre apenas três valores possíveis por classe, um por
cluster. A matriz de confusão mostra 1.044 de 1.568 leituras `Medium_Load` atribuídas
a `Maximum_Load`. A classificação por cluster é uma avaliação pós-hoc, não um novo
classificador supervisionado treinado para otimizar essas métricas. Fonte:
`modelagem_classificacao_externa_teste.csv` e resultados por leitura.

| Referência no teste | ARI | NMI |
| --- | --- | --- |
| modelo selecionado (`regime` / K-Means) | 0,342 | 0,304 |
| sensibilidade (`regime_with_calendar` / K-Means) | 0,355 | 0,315 |
| regra de maioria de calendário (hora × situação da semana, usa rótulos do treino) | 0,494 | 0,342 |

A concordância é moderada e inferior à de uma regra puramente de calendário. Isso é
esperado: `Load_Type` é uma tabela horária de tarifa, enquanto os regimes descrevem o
estado elétrico da planta. O modelo separa ociosidade de produção, mas não separa carga
média de carga máxima, que eletricamente são ambas produção (92% do regime ocioso
indutivo é `Light_Load`).

!!! note "Desvio de protocolo"
    O protocolo especificava a referência de calendário com hora, situação da semana
    **e mês**. Novembro e dezembro não estão presentes no treino, então essa regra se
    reduz a uma constante (ARI = 0). A referência usa hora e situação da semana. Isso
    afeta apenas a referência, não a seleção do modelo, que já estava congelada.

`Load_Type` também pode ser usado em uma tabela pós-hoc para descrever quais regimes de
carga aparecem entre os sinais. Essa tabela não é métrica de anomalia: não deve calibrar
o limiar, equalizar taxas entre classes nem transformar um alerta em falha confirmada.

## Filtro de transição (modelo v1.1)

A seção 10 do notebook 03 suprime os alertas nas fronteiras de regime, mantendo o limiar da v1.0. A
regra de decisão exigia que os alertas de fronteira fossem pelo menos 3× a participação
das leituras de fronteira na validação; o aumento observado foi de 9,5×. A regra foi
escrita depois de o notebook 04 já ter mostrado que 88% dos alertas da validação (90% no
teste) caem em fronteiras, então ela documenta a decisão em vez de testá-la às cegas.

| Divisão | Alertas v1.0 | Alertas v1.1 | Taxa v1.1 |
| --- | --- | --- | --- |
| validação | 59 | 7 | 0,12% |
| teste | 49 | 5 | 0,09% |

Dez dos 12 alertas restantes compartilham uma assinatura: carga média (10–31 kWh) com
corrente adiantada em manhãs de fim de semana, o mesmo perfil do episódio de 22 de maio.
Os outros dois também são leituras de fim de semana com carga média: sábado, 6 de
outubro, às 12:30 (regime de produção, 24 kWh) e domingo, 21 de outubro, às 16:30. No
episódio noturno de julho, 7 de 29 alertas são suprimidos porque o próprio evento cria
mudanças de regime; restam 22. Recalibrar o limiar nas leituras fora de fronteira, em
vez disso, produziria 54 alertas na validação, em sua maioria marginais.

Ressalvas: a análise de recorrência e as proporções de fronteira do notebook 04
consideraram o ano inteiro, teste incluído, antes desta mudança, então os números da
v1.1 no teste não são uma avaliação independente do filtro; e, em operação contínua, um alerta é
atrasado em 15 minutos, porque uma fronteira precisa da leitura seguinte.
`is_anomaly_raw` e `anomaly_score` continuam publicados.

## Salvaguardas respeitadas

- `Load_Type` não entrou no ajuste dos modelos de regimes ou de anomalias. Sua
  cardinalidade definiu três grupos, e sua inspeção no treino apoiou a exclusão do
  calendário das variáveis de regime. Após a seleção, os rótulos do treino também
  definiram o mapeamento pós-hoc de clusters para classes usado na avaliação externa;
- o limiar de anomalia foi escolhido na validação e relatado no teste;
- PCA/t-SNE não foram usados para seleção; todas as métricas estão no espaço
  transformado.

## Limitações

- um ano de dados, então a sazonalidade não pode ser validada entre ciclos;
- os nomes dos regimes vêm da interpretação dos perfis e precisam de validação com a
  equipe da planta;
- não há rótulos de falha: a precisão das anomalias não pode ser medida.
