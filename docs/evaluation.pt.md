# Avaliação

A avaliação final foi executada uma única vez no período de teste congelado
(novembro–dezembro), depois que o modelo, o pré-processamento e o limiar de anomalia
foram fixados. Os valores vêm de `artifacts/metadata/final_metrics.json`.

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

## Evidências de anomalias

- o top 1% da validação se sobrepõe em 87%, em média, entre cinco sementes (Jaccard);
- cerca de 40% dos alertas da validação se repetem no mesmo dia da semana e horário em
  três ou mais semanas (por exemplo, domingo às 08:45 todas as semanas). É mais provável
  que sejam eventos programados do que falhas, e eles devem ser revisados com a operação
  da planta;
- a taxa de 1% é uma premissa operacional: não há rótulos de falha para estimá-la.

## Concordância externa com `Load_Type`

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

## Filtro de transição (modelo v1.1)

O notebook 05 suprime os alertas nas fronteiras de regime, mantendo o limiar da v1.0. A
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

- `Load_Type` nunca entrou em um ajuste e foi usado para concordância somente após o
  congelamento. Foi inspecionado apenas no treino, no notebook 02b, e essa inspeção
  definiu uma escolha de desenho: excluir o calendário das variáveis de regime (D3). É
  um uso deliberado e declarado do rótulo antes do congelamento;
- o limiar de anomalia foi escolhido na validação e relatado no teste;
- PCA/t-SNE não foram usados para seleção; todas as métricas estão no espaço
  transformado.

## Limitações

- um ano de dados, então a sazonalidade não pode ser validada entre ciclos;
- os nomes dos regimes vêm da interpretação dos perfis e precisam de validação com a
  equipe da planta;
- não há rótulos de falha: a precisão das anomalias não pode ser medida.
