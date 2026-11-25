# Quadro PBL

## O que sabemos

- o conjunto de dados da indústria siderúrgica da UCI está disponível localmente;
- ele contém 35.040 observações de 15 minutos e 11 colunas;
- não há valores ausentes nem linhas exatamente duplicadas no arquivo local;
- `Load_Type` contém três categorias;
- os artefatos e baselines da EDA podem ser reproduzidos localmente;
- arquivos gerados e pesados são excluídos do Git.

## O que estamos investigando

- se os três regimes não supervisionados são estáveis e operacionalmente interpretáveis;
- como efeitos de calendário e variáveis elétricas correlacionadas afetam a segmentação;
- quais observações extremas são comportamentos legítimos de um regime;
- como a ordenação das anomalias muda conforme as premissas e o tempo;
- quais escolhas de preparação e modelo se generalizam além da EDA.

## Plano de trabalho

| Etapa | Evidência | Situação |
| --- | --- | --- |
| EDA | dicionário, figuras, tabelas, hipóteses | revisão em andamento |
| Preparação | transformações ajustadas e seguras contra vazamento | concluída; aguardando aprovação da equipe |
| Modelagem | comparação reproduzível e estabilidade | concluída |
| Avaliação | métricas congeladas e avaliação externa | concluída |
| Publicação | manifesto, modelo final, aplicação | concluída (modelo v1.1) |
| Revisão da equipe | decisões, nomes dos regimes, triagem de alertas | aguardando pessoas |

## Reflexão

Os três regimes são estáveis (ARI de bootstrap 0,999) e eletricamente interpretáveis,
mas descrevem o estado elétrico da planta, e não a tabela horária de tarifa de
`Load_Type`. Os nomes dos regimes, as explicações causais e a taxa de alertas ainda
precisam da contribuição da planta e da operação.
