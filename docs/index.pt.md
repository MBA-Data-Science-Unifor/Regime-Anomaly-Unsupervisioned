# Consumo de Energia na Indústria Siderúrgica — Regimes e Anomalias

Este projeto investiga regimes operacionais e observações incomuns de consumo de energia
em um conjunto de dados de uma indústria siderúrgica sul-coreana. A análise é não
supervisionada: `Load_Type` fornece apenas a cardinalidade conhecida de três regimes e
não é usado como variável de entrada nem como rótulo de treinamento.

## Situação atual

| Componente | Situação |
| --- | --- |
| Conjunto de dados bruto | disponível localmente; excluído do Git |
| EDA | implementada e documentada |
| Dicionário de dados | gerado localmente |
| Figuras e tabelas exploratórias | geradas localmente; excluídas do Git |
| Notebook de preparação | implementado; seleção em revisão |
| Comparação final de modelos | pendente |
| Avaliação congelada | pendente |
| Streamlit | estrutura somente leitura disponível |

Os resultados atuais de agrupamento e anomalias são evidências exploratórias, não uma
seleção final de modelo nem uma validação de negócio.

## Fluxo de trabalho

1. entender a granularidade e a qualidade das medições;
2. examinar distribuições individuais e o comportamento temporal;
3. estudar relações sem usar `Load_Type`;
4. projetar o espaço de variáveis com PCA e t-SNE;
5. inspecionar baselines de K-Means e GMM com três regimes;
6. inspecionar sinais de anomalia do Isolation Forest;
7. levar decisões aprovadas para preparação, modelagem e avaliação.

Consulte [Descobertas iniciais](initial-findings.md) para ver as evidências disponíveis.
Consulte [Referências técnicas](references.md) para as bibliotecas, APIs e fontes oficiais.
