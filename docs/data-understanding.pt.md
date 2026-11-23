# Entendimento dos Dados

## Unidade de análise

Cada linha representa uma observação industrial de energia de 15 minutos. Há 35.040
linhas, valor consistente com 365 dias multiplicados por 96 intervalos diários.

## Grupos de variáveis

| Grupo | Variáveis | Papel |
| --- | --- | --- |
| Tempo | date, NSM | instante e segundos desde a meia-noite |
| Energia | Usage_kWh | consumo de energia ativa |
| Energia reativa | kVarh atrasado e adiantado | comportamento elétrico |
| Emissões | CO2(tCO2) | medida informada de CO2 |
| Qualidade da potência | fator de potência atrasado e adiantado | eficiência/contexto elétrico |
| Calendário | WeekStatus, Day_of_week | contexto operacional |
| Referência externa de regime | Load_Type | somente cardinalidade e avaliação posterior |

## Verificações de qualidade confirmadas

- 35.040 linhas e 11 colunas;
- nenhum valor ausente no CSV local;
- nenhuma linha exatamente duplicada;
- 96 observações por dia completo;
- três categorias de `Load_Type`;
- variáveis numéricas com escalas muito diferentes e distribuições assimétricas.

## Cuidados importantes

Os metadados da UCI e o nome da coluna de CO2 usam descrições de unidade potencialmente
inconsistentes; o dicionário preserva os metadados oficiais e essa questão deve ser
resolvida antes do relatório final. A data é interpretada no formato dia-primeiro.
`Load_Type` é excluído das relações entre variáveis e do ajuste dos modelos.
