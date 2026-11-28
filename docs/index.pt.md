# Consumo de Energia na Indústria Siderúrgica — Regimes e Anomalias

Este projeto investiga regimes operacionais e observações incomuns de consumo de energia
em um conjunto de dados de uma indústria siderúrgica sul-coreana. A análise é não
supervisionada: `Load_Type` fornece a cardinalidade de três regimes e apoia decisões
de desenho, mas não é entrada nem rótulo de treinamento dos modelos. Após a seleção,
os rótulos do treino também são usados no mapeamento de clusters para avaliação externa.
Uma classificação supervisionada experimental de `Load_Type` é uma tarefa separada e
complementar, apresentada no notebook 03 e revista no notebook 04.

## Situação atual

| Componente | Situação |
| --- | --- |
| Conjunto de dados bruto | CSV versionado no Git |
| EDA | implementada e documentada |
| Dicionário de dados | gerado localmente |
| Figuras e tabelas exploratórias | geradas localmente; excluídas do Git |
| Notebook de preparação | implementado como 02; decisões aguardando aprovação da equipe |
| Comparação final de modelos | concluída: K-Means, três regimes, apenas variáveis elétricas |
| Avaliação temporal | concluída em novembro–dezembro, com exposição prévia do período na EDA |
| Detector de anomalias | Isolation Forest com filtro de transição (modelo v1.1) |
| Streamlit | painel de monitoramento sobre os resultados publicados; executa o modelo em arquivos CSV enviados |

O modelo está selecionado e avaliado, mas ainda não foi validado pelo negócio: os nomes
dos regimes, a taxa de alertas e os próprios alertas aguardam revisão da planta e da
operação (consulte [Revisão da equipe](team-review.md) e [Situação](status.md)).

## Fluxo de trabalho

1. entender a granularidade e a qualidade das medições;
2. examinar distribuições individuais e o comportamento temporal;
3. estudar relações sem usar `Load_Type`;
4. projetar o espaço de variáveis com PCA e t-SNE;
5. inspecionar baselines de K-Means e GMM com três regimes;
6. inspecionar sinais de anomalia do Isolation Forest e seu contexto operacional;
7. comparar um baseline global com detecção contextual;
8. levar decisões aprovadas para preparação, modelagem e avaliação.

Consulte [Descobertas iniciais](initial-findings.md) para ver as evidências exploratórias,
e [Modelagem](modeling.md) e [Avaliação](evaluation.md) para os resultados finais.
Consulte [Referências técnicas](references.md) para as bibliotecas, APIs e fontes oficiais.
O [Histórico do projeto](project-history.md) reúne as percepções, decisões e pendências
identificadas ao longo das análises e revisões.
O [Canvas PBL](pbl/problem-canvas.md) responde às 11 perguntas de negócio, dados,
critérios de sucesso e ações esperadas; o [Quadro PBL](pbl/pbl-board.md) acompanha
as pendências.
