# Revisão da Equipe

Três itens pendentes dependem de pessoas, não de código. Esta página e
`artifacts/notebooks/04_Review.ipynb` preparam cada um deles para que possa ser decidido
em uma única reunião. O notebook apenas lê os artefatos publicados; nada é reajustado.

Convenção de horário: cada leitura cobre 15 minutos. Os horários abaixo são mostrados
como intervalos (`12:00–12:15`), o período que a leitura mede.

## 1. Decisões para aprovação (equipe do projeto)

| # | Decisão | Evidência | Se rejeitada |
| --- | --- | --- | --- |
| D1 | Mover a leitura das 24:00 para a meia-noite seguinte | 365 saltos para trás com uma interpretação ingênua | não há alternativa válida; a ordenação e a divisão quebram |
| D2 | Divisão cronológica jan–ago / set–out / nov–dez | leituras adjacentes são dependentes | refazer os notebooks 02 e 03 |
| D3 | Calendário **excluído** das variáveis de regime | uma regra de maioria por calendário reproduz ~92% do `Load_Type` de treino (dentro da amostra, ~1.500 faixas; só hora + status da semana + mês: 87%); com calendário, os GMMs ficam instáveis (silhueta 0,82 → 0,38, mas medida em 5 contra 10 dimensões, logo não estritamente comparável) | trocar para `regime_with_calendar` (já medido) |
| D4 | CO2 excluído | Pearson 0,99 com o consumo, oito valores distintos | o consumo pesa em dobro nas distâncias |
| D5 | `log1p` na energia, `log1p(100 − PF)` no fator de potência | assimetria do consumo 1,14 → 0,43 | refazer a seleção |
| D6 | Extremos mantidos | anomalias são um objetivo do projeto | o detector perde os casos incomuns |
| D7 | Regra de seleção (ARI de bootstrap ≥ 0,80, menor grupo ≥ 5%, melhor silhueta) | fixada antes dos resultados | resultado inalterado: o K-Means também lidera em estabilidade temporal |
| D8 | Taxa de alertas de 1% calibrada na validação | 0,84% no teste; Jaccard 0,87 entre sementes | alterar `ALERT_RATE` no notebook 03 |
| D9 | Referência de calendário sem mês (desvio de protocolo) | nov–dez ausentes do treino | afeta apenas a referência |

D3 e D8 são as que mais mudam a leitura dos resultados.

## 2. Nomes dos regimes (equipe da planta)

As evidências sustentam os três nomes:

- **ocioso indutivo** — um bloco noturno longo e regular (episódio mediano de 9,75 h),
  sem corrente adiantada;
- **ocioso capacitivo** — episódios curtos, 496 de 838 entre dois blocos de produção
  (pausas, com pico às 12:00 em dias úteis) e 267 entre a produção e o bloco noturno (fim
  de turno); cobre boa parte do dia nos fins de semana;
- **produção** — horário de trabalho em dias úteis (~94% das leituras das 08:00 às
  17:00, exceto 12:00–13:00).

**A corrente adiantada segue o relógio, não a carga.** Entre as leituras de baixa carga
(< 10 kWh), a corrente adiantada está presente em 0% antes das 08:30, 35% em
08:30–08:45, 100% de 08:45–09:00 até 21:45–22:00, 65% em 22:00–22:15 e 3% depois. À
noite, com a mesma carga, ela aparece em apenas 1,4%. Isso é consistente com uma
compensação de potência reativa (um banco de capacitores) ligada por temporizador de
cerca de 08:40 a 22:05.

**Perguntas para a equipe da planta**

1. Existe uma pausa programada por volta de 12:00–13:00 nos dias úteis?
2. O banco de capacitores é acionado por temporizador, aproximadamente das 08:40 às
   22:05, inclusive nos fins de semana?
3. A planta opera parcialmente durante o dia aos sábados e domingos?
4. Os nomes são adequados, ou existem termos internos melhores (por exemplo, "parada
   noturna", "espera compensada")?

Se a pergunta 2 for confirmada, o regime capacitivo é uma janela de
**sobrecompensação**: os capacitores permanecem ligados enquanto a carga está baixa, o
que pode ser faturado como excedente de energia reativa adiantada.

## 3. Triagem de alertas (operação)

Cada alerta recebe duas marcações objetivas:

- **fronteira** — seu regime difere do da leitura anterior ou seguinte;
- **recorrente** — o mesmo dia da semana e intervalo gerou alerta em pelo menos três
  semanas distintas.

**A maioria dos alertas são transições de regime.** As leituras de fronteira são 11,1%
de todas as leituras, mas 81,3% dos alertas (88% na validação, 90% no teste). Uma leitura
de 15 minutos que abrange uma mudança de estado fica a meio caminho entre os dois estados
e parece incomum. Os dois padrões mais frequentes são o desligamento do capacitor
(22:00–22:15, até 32 semanas) e o início da pausa dos dias úteis (12:00–12:15, 20–29
semanas).

| Prioridade | Categoria sugerida | Alertas | Treino | Validação | Teste |
| --- | --- | --- | --- | --- | --- |
| 1 | isolado — investigar | 38 | 36 | 2 | 0 |
| 2 | padrão recorrente | 70 | 60 | 5 | 5 |
| 3 | transição pontual | 50 | 30 | 13 | 7 |
| 4 | transição programada | 421 | 345 | 39 | 37 |

Os escores do treino são dentro da amostra (o Isolation Forest foi ajustado no treino),
então a taxa de alertas do treino (~2%) não é comparável com a da validação e do teste
(~1%).

**Os alertas isolados formam dois episódios que merecem investigação:**

- **15–23 de julho, 02:15–03:00** — corrente adiantada à noite na maioria das noites,
  fora do horário dos capacitores. Hipótese: compensação deixada ligada durante a noite
  por cerca de uma semana (mudança no temporizador, manutenção ou falha);
- **22 de maio, 09:00–10:00** — carga média (~25 kWh) com corrente adiantada.

**Planilha de triagem.** `artifacts/tables/revisao_alertas_triagem.csv` lista todos os
579 alertas por prioridade e escore, com uma coluna `parecer_operacao` vazia. Valores
permitidos: `rotina` (evento programado conhecido), `transicao` (mudança de estado
normal), `falha` (problema real de equipamento ou processo), `investigar` (desconhecido),
`dado` (erro de medição ou de registro). Depois de preenchida, a precisão do detector
poderá ser medida pela primeira vez.

## Filtro de transição (aplicado na v1.1)

O notebook 05 aplicou o filtro de fronteira: 59 → 7 alertas na validação e 49 → 5
alertas no teste. A planilha de triagem mantém todos os 579 alertas não filtrados, para
que a operação ainda possa confirmar que as transições não são de interesse; se forem,
republicar com `transition_filter=False`.
