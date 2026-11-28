# Quadro PBL

O [Canvas do Problema](problem-canvas.md) responde às 11 perguntas de negócio, dados,
critérios e ações esperadas. Este quadro acompanha as evidências e as pendências.

## O que sabemos

- o conjunto de dados da indústria siderúrgica da UCI está disponível localmente;
- ele contém 35.040 observações de 15 minutos e 11 colunas;
- não há valores ausentes nem linhas exatamente duplicadas no arquivo local;
- `Load_Type` contém três categorias;
- os artefatos e baselines da EDA podem ser reproduzidos localmente;
- o CSV bruto é versionado; os artefatos gerados são excluídos do Git;
- há uma comparação supervisionada complementar de `Load_Type` no notebook 03.

## O que estamos investigando

- se os três regimes não supervisionados são estáveis e operacionalmente interpretáveis;
- como efeitos de calendário e variáveis elétricas correlacionadas afetam a segmentação;
- quais observações extremas são comportamentos legítimos de um regime;
- como a ordenação das anomalias muda conforme as premissas e o tempo;
- quais escolhas de preparação e modelo se generalizam além da EDA;
- quais alertas e leituras sem alerta a operação considera relevantes;
- como acordar meta de utilidade, prazo e amostragem para um piloto.

## Plano de trabalho

| Etapa | Evidência | Situação |
| --- | --- | --- |
| EDA | dicionário, figuras, tabelas, hipóteses | revisão em andamento |
| Preparação | transformações ajustadas e seguras contra vazamento | concluída; aguardando aprovação da equipe |
| Modelagem | comparação reproduzível e estabilidade | concluída |
| Avaliação histórica | métricas internas, concordância externa e teste retrospectivo | concluída com ressalvas; período independente pendente |
| Publicação | manifesto, modelo final, aplicação | concluída (modelo v1.1) |
| Revisão da equipe | decisões, nomes dos regimes, triagem de alertas | aguardando pessoas |

## Reflexão

Os três regimes são estáveis (ARI de bootstrap 0,999) e eletricamente interpretáveis,
mas descrevem o estado elétrico da planta, e não a tabela horária de tarifa de
`Load_Type`. Os nomes dos regimes, as explicações causais e a taxa de alertas ainda
precisam da contribuição da planta e da operação.

## Decisões e evidências pendentes

1. Confirmar usuários, responsáveis, objetivo de negócio e nome oficial da trilha.
2. Acordar critério de utilidade, prazo, custo e amostragem antes de qualquer piloto.
3. Obter pareceres para alertas e uma amostra de leituras sem alerta; decidir se o
   filtro de transições deve permanecer ativo.
4. Avaliar decisões e limiares previamente fixados em período posterior independente.
