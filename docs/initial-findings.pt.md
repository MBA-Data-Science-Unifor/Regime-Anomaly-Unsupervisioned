# Descobertas Iniciais

!!! warning "Evidência exploratória"
    Estas observações vêm da EDA atual e de artefatos locais regenerados. Elas não são
    resultados de uma avaliação congelada nem recomendações de produção.

## Perfil do conjunto de dados

- 35.040 medições e 11 colunas;
- nenhum valor ausente ou linha exatamente duplicada;
- frequência de 15 minutos ao longo de 2018;
- 25.056 observações em dias úteis e 9.984 em fins de semana;
- contagens de `Load_Type`: 18.072 `Light_Load`, 9.696 `Medium_Load` e 7.272
  `Maximum_Load`.

## Impressões das distribuições

Consumo, energia reativa atrasada, energia reativa adiantada e CO2 têm assimetria à
direita. O fator de potência adiantado tem forte assimetria à esquerda. A regra do IQR
marca cerca de 23,8% das observações do fator de potência adiantado e 22,1% das
observações de energia reativa adiantada como extremas; isso reflete o formato das
distribuições e não deve ser interpretado como equivalente a uma anomalia operacional.

## Impressões das relações

Os diagnósticos atuais de Spearman mostram:

- forte associação positiva entre `Usage_kWh` e CO2, aproximadamente 0,88;
- associação positiva entre consumo e energia reativa atrasada, aproximadamente 0,64;
- forte associação inversa entre energia reativa adiantada e fator de potência
  adiantado, aproximadamente -0,97;
- estrutura clara de hora do dia e dia útil/fim de semana no consumo médio.

Essas relações motivam escalonamento, verificações de redundância e testes de
estabilidade temporal.

![Matriz de correlação de Pearson das variáveis elétricas numéricas](assets/images/correlation-matrix.png)

*Figura 1 — Correlação de Pearson calculada a partir das variáveis numéricas brutas, com
`Load_Type` excluído. Ela sustenta o alerta de redundância entre consumo e CO2 e a forte
relação inversa entre energia reativa adiantada e fator de potência adiantado; correlação
não implica causalidade.*

![Consumo médio de energia por mês e hora](assets/images/consumption-month-hour.png)

*Figura 2 — Média de `Usage_kWh` por mês e hora. Os blocos recorrentes da manhã e da
tarde sustentam a impressão de padrão temporal, mas o mapa isoladamente não identifica
sua causa operacional.*

## Impressões multivariadas

Os dois primeiros componentes do PCA explicam aproximadamente 73,4% da variância do
espaço transformado. PCA e t-SNE mostram regiões estruturadas, mas as projeções não
provam a existência nem o significado de negócio dos grupos.

Nos diagnósticos de K-Means em uma amostra reproduzível, K=3 apresenta a maior silhueta
testada, aproximadamente 0,449. O baseline completo com três grupos contém atualmente
13.074, 14.378 e 7.588 observações. Isso apoia a continuidade da investigação, mas não é
uma validação externa.

![Diagnósticos de cotovelo e silhueta do K-Means](assets/images/kmeans-diagnostics.png)

*Figura 3 — Diagnósticos armazenados do K-Means no notebook 01. K=3 é simultaneamente a
hipótese do problema e a maior silhueta entre K=2…8 nesta execução; isso sustenta uma
segmentação plausível, não equivalência com as categorias externas de `Load_Type`.*

No diagnóstico de GMM, o BIC continua melhorando até os oito componentes testados,
enquanto o modelo condicionado pelo problema permanece fixado em três. Isso sugere uma
subestrutura estatística dentro dos três regimes operacionais, não uma evidência de que
o problema de negócio tenha oito regimes.

O Isolation Forest sinaliza 701 observações sob uma taxa de contaminação presumida de
2%. Esses registros são candidatos à investigação, não falhas confirmadas.

## Próximas verificações

- reproduzir a preparação fora do notebook de EDA;
- medir a estabilidade dos grupos com reamostragens e divisões temporais;
- testar a sensibilidade a grupos de variáveis e transformações;
- definir um protocolo congelado de avaliação externa;
- resolver a descrição da unidade de CO2;
- evitar transformar prematuramente rótulos exploratórios em treinamento supervisionado.

## Evidências por notebook

| Notebook | Evidência disponível atualmente | Situação da interpretação |
| --- | --- | --- |
| `01_EDA.ipynb` | auditoria dos dados, distribuições, perfis de calendário, correlações, PCA/t-SNE, K-Means, GMM e Isolation Forest | exploratória |
| `02_preprocessing.ipynb` | divisão temporal, configurações de variáveis, pré-processamento ajustado, PCA, estabilidade dos grupos e artefatos exportados | experimental; seleção não congelada |
| `03_Modeling.ipynb` | estrutura reservada e TODO | ainda sem resultado de modelo |

A execução armazenada da EDA também informa ausência de timestamps duplicados, intervalo
constante de 15 minutos e picos recorrentes de atividade aproximadamente entre 9h–11h e
14h–17h. As medianas em dias úteis são 7,60 kWh para consumo e 5,80 kVarh para energia
reativa atrasada, contra 3,46 kWh e 3,02 kVarh nos fins de semana. Esses são padrões
operacionais descritivos, não explicações causais.

## Impressões do notebook de pré-processamento

A execução armazenada de `02_preprocessing.ipynb` usa uma divisão cronológica 80/20: o
treinamento vai de 01/01/2018 a 19/10/2018 e o teste vai de 20/10/2018 a 31/12/2018.

| Configuração de variáveis | Silhueta | ARI contra as categorias externas |
| --- | ---: | ---: |
| Baseline numérico | 0,6361 | 0,3482 |
| Numéricas + hora + mês | 0,6361 | 0,3482 |
| Numéricas + `Day_of_week` | 0,4680 | 0,3476 |
| Numéricas + `Day_of_week` + PCA 90% | 0,5409 | 0,3478 |

![Comparação dos diagnósticos armazenados do pré-processamento](assets/images/preprocessing-diagnostics.png)

*Figura 4 — Escores armazenados pelo notebook 02. O gráfico torna visível a tensão da
seleção: o baseline numérico possui a maior silhueta, enquanto o ARI externo varia muito
pouco entre as configurações testadas.*

O pipeline PCA ajustado mantém seis componentes para explicar 90% da variância e informa
correlação máxima entre componentes igual a 0,0 após arredondamento. Entre subamostras, a
configuração final com três grupos apresenta estabilidade ARI de 0,9983 ± 0,0015, uma
forte evidência de repetibilidade para esse pipeline e protocolo de amostragem específicos.

As variáveis de reporte excluídas do ajuste ainda distinguem os grupos: a média de CO2
varia de 0,000 a 0,031 tCO2, enquanto a média do fator de potência adiantado varia de
aproximadamente 38,716 a 99,991. Isso apoia a interpretação posterior ao ajuste, mas não
estabelece validade causal ou de negócio.

!!! caution "A seleção permanece em aberto"
    O baseline numérico tem silhueta maior que a configuração PCA selecionada no
    notebook. As variáveis de hora e mês também não alteram os escores armazenados do
    baseline. A escolha final precisa, portanto, de uma justificativa documentada com
    múltiplos critérios e de uma verificação de que cada candidato recebeu as colunas
    pretendidas. O ARI é apresentado apenas como diagnóstico externo e não deve orientar
    o ajuste não supervisionado.

## Situação do notebook de modelagem

`03_Modeling.ipynb` declara explicitamente que não possui resultados na versão atual.
Nenhum desempenho de modelo final, limiar de produção ou avaliação externa congelada
deve ser inferido a partir dos notebooks de EDA ou pré-processamento.
