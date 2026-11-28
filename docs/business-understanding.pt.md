# Entendimento do Problema

## Contexto

A demanda industrial de eletricidade varia conforme a intensidade da produção, a
potência reativa, os efeitos de calendário e o comportamento dos equipamentos. Entender
regimes operacionais recorrentes pode apoiar o planejamento energético e ajudar a
priorizar medições incomuns para investigação.

## Objetivo

Construir uma análise não supervisionada e reproduzível do conjunto de dados *Steel
Industry Energy Consumption* que:

- descreva o comportamento da energia e do fator de potência;
- investigue uma estrutura compatível com três regimes operacionais;
- sinalize observações incomuns sem afirmar que representam falhas;
- produza evidências para a comparação posterior de modelos e para uma aplicação
  somente leitura.

Como tarefa complementar, o projeto testa classificação supervisionada de `Load_Type`
usando medições do mesmo intervalo. As abordagens respondem a perguntas distintas;
a classificação não valida os alertas de anomalia.

O [Canvas PBL](pbl/problem-canvas.md) reúne as 11 perguntas de contexto, dor, metas,
dados, riscos e ações, distinguindo hipóteses de negócio das evidências verificadas.

## Perguntas orientadoras

- Quais variáveis melhor distinguem comportamentos operacionais baixo, médio e alto?
- Os três regimes esperados são geometricamente coerentes sem o uso de seus rótulos?
- Como hora, dia da semana e fim de semana afetam os regimes?
- Quais observações são globalmente incomuns?
- Quais descobertas permanecem estáveis ao longo do tempo e de reamostragens?

## Limites

O trabalho não infere causalidade, falha de equipamento, economia financeira nem
qualidade da produção. Os valores de `Load_Type` não são usados no ajuste não
supervisionado. Nenhum modelo supervisionado, limiar operacional ou recomendação de
produção está aprovado nesta etapa.
