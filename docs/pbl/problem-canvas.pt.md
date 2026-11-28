# Canvas PBL — problema, dados e decisões

Este canvas responde às 11 perguntas do projeto. Ele separa **evidência observada**,
**interpretação** e **proposta pendente**: a base é pública e não registra uma demanda
ou autorização da empresa para implantação. O estudo é acadêmico, com dados históricos.

| Equipe | Trilha |
| --- | --- |
| Alexandre Franco — análise de dados e modelagem; Rodrigo Franco — engenharia de dados; Caio Cunha Franco — engenharia de IA. | Análise de consumo energético, agrupamento e detecção de anomalias, com classificação supervisionada complementar. **Nome oficial da trilha:** não informado; confirmar com a equipe. |

## 1. Contexto de negócio

**Que organização é essa, o que faz e quem decide o quê?**

A fonte descreve medições de energia da DAEWOO Steel Co. Ltd, uma indústria siderúrgica
em Gwangyang, Coreia do Sul. O projeto analisa esses dados para entender perfis de
consumo e leituras incomuns; não representa um trabalho contratado pela empresa.

Os potenciais usuários são analistas de energia e equipes de operação. A equipe do
projeto decide a metodologia e apresenta evidências; uma eventual equipe da planta
decidiria se os regimes fazem sentido, quais alertas investigar e se o filtro de
transições é adequado. **Os responsáveis reais e sua autoridade não foram informados.**

Evidências: [Fonte dos dados](../data-source.md),
[Entendimento do problema](../business-understanding.md) e
[Revisão da equipe](../team-review.md).

## 2. A dor

**O que dói hoje por não existir essa segmentação? Quem sofre com isso?**

Como hipótese de negócio, sem uma visão organizada dos perfis de energia, analistas e
operação podem ter dificuldade para distinguir padrões recorrentes de leituras que
merecem investigação. A falta de contexto também pode gerar uma lista extensa de
alertas em transições comuns. O projeto pretende apoiar a priorização dessas análises.

**Limite:** não foi demonstrado que a empresa não possui segmentação, que enfrenta
esse problema atualmente ou que há impacto financeiro. São hipóteses a validar com
usuários da planta.

## 3. Objetivo de negócio

**O que a organização quer realizar, além da técnica?**

Apoiar a compreensão do comportamento energético e a priorização de leituras incomuns
para revisão, tornando mais clara a diferença entre perfis recorrentes e situações que
merecem apuração. Uma possível utilização é organizar a investigação da operação;
economia de energia, redução de falhas e ganhos financeiros **não foram demonstrados**.
O objetivo proposto ainda precisa de concordância dos responsáveis pela operação.

## 4. Critério de sucesso do negócio

**Como a diretoria saberia se deu certo? Métrica e meta.**

Nenhuma meta de negócio foi aprovada por uma diretoria ou medida na planta. Para uma
avaliação futura, propomos que a operação registre o parecer para cada caso revisado e
meça a proporção de alertas considerados úteis para investigação:

> alertas avaliados como úteis ÷ alertas efetivamente revisados × 100.

Como **proposta de piloto**, em um período a definir, revisar os **20 alertas de maior
escore mantidos pelo filtro**, ou todos se houver menos de 20, além de uma amostra de leituras sem alerta,
e registrar um parecer para **100% dos casos selecionados**. Essa meta mede a
conclusão da triagem, não o sucesso do detector. A meta mínima de utilidade, o tamanho
e o método da amostra sem alerta, o prazo e o responsável devem ser acordados com a
operação antes do piloto. A precisão e a sensibilidade só poderão ser estimadas com
rótulos adequados e uma amostragem documentada.

## 5. Meta de mineração

**Qual é o resultado técnico esperado?**

- **Agrupamento:** investigar três perfis elétricos com K-Means e GMM, sem usar os
  valores de `Load_Type` no ajuste. O número três foi definido pela cardinalidade
  conhecida do rótulo e é uma restrição externa, não uma descoberta independente.
- **Anomalias:** ordenar leituras por atipicidade com Isolation Forest, com limiar e
  filtro explicitados, para investigação posterior.
- **Comparação supervisionada:** usar KNN e alternativas para classificar `Load_Type`
  com as medições do mesmo intervalo e comparar com referências. Essa tarefa usa
  rótulos no treino e não valida falhas nem prevê consumo antes da medição.
- **Redução de dimensionalidade:** usar PCA e t-SNE para visualização exploratória;
  suas projeções não definem, por si só, o número de grupos.

Evidências: [Modelagem](../modeling.md) e [Avaliação](../evaluation.md).

## 6. Critério de sucesso técnico

**Que valores e verificações tornam o resultado tecnicamente aceitável?**

| Critério | Regra do projeto | Resultado ou situação |
| --- | --- | --- |
| Número de grupos | Exatamente **3** na hipótese principal; não é um máximo inferido dos dados. | Atendido pelo desenho dos candidatos. |
| Tamanho do menor grupo | Pelo menos **5%** na validação. | K-Means: **21,3%**. |
| Estabilidade por bootstrap | ARI médio de pelo menos **0,80**. | K-Means: **0,999**. |
| Silhueta | Escolher a maior entre os candidatos elegíveis no conjunto principal; **não foi definida silhueta mínima absoluta**. | K-Means: **0,823** na validação e **0,768** no teste histórico. |
| Alertas de anomalia | Percentil 99 na validação, premissa de aproximadamente **1% bruto**. | **59/5.856** na validação; não é precisão nem limite comprovado de ruído. |
| Classificação supervisionada | Comparar F1 macro e desempenho por classe com referências temporais; não há meta mínima aprovada. | KNN: F1 macro **0,919** na validação e **0,593** no teste histórico. |

O K-Means atende à regra de seleção interna. Isso não comprova utilidade operacional.
Não existe percentual máximo de ruído/falsos positivos validado: faltam rótulos de
falha e definição de custos. Como a EDA examinou todo o ano e o filtro foi estudado
após consulta ao teste, o teste histórico não é plenamente independente. A avaliação
em período posterior é uma pendência, não um resultado alcançado.

## 7. Entidade de análise

**O que é uma linha da base?**

Uma linha representa uma leitura elétrica de **15 minutos**, acompanhada do contexto
de calendário e de `Load_Type`. A data/hora da fonte marca o **fim do intervalo**;
as leituras de `00:00` que encerram o dia são corrigidas para a meia-noite seguinte
antes da ordenação cronológica. Os 15 minutos vizinhos são dependentes, portanto a
separação temporal é mais apropriada que uma divisão aleatória para este protocolo.

## 8. Fonte e volume dos dados

**Origem, período, registros, atributos e permissões de uso.**

| Item | Descrição |
| --- | --- |
| Fonte | [UCI Steel Industry Energy Consumption](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption), DOI 10.24432/C52G8C. |
| Período | Leituras de 2018; após a correção, timestamps de 01/01/2018 00:15 a 01/01/2019 00:00. |
| Volume | **35.040 linhas** e **11 colunas**, incluindo data e `Load_Type`. |
| Partições | Treino: **23.328** leituras (jan–ago); validação: **5.856** (set–out); teste: **5.856** (nov–dez). A leitura que encerra um dia fica na partição desse dia. |
| Qualidade verificada | Metadados da preparação registram zero nulos, timestamps duplicados ou intervalos irregulares após correção. |
| Uso | A fonte informa licença **CC BY 4.0**; manter atribuição e cumprir seus termos. A licença da base não é autorização para operar sistemas da planta. |

Consulte [Fonte dos dados](../data-source.md) e
[Preparação](../data-preparation.md) para proveniência e transformações.

## 9. Perguntas orientadas a dados

**De três a cinco perguntas específicas, mensuráveis, relevantes e delimitadas no tempo.**

1. **Regimes:** nas leituras de set–out de 2018, os três grupos elétricos selecionados
   apresentam menor grupo ≥ 5% e qual é a silhueta? Registrar também a estabilidade
   por bootstrap a partir do treino de jan–ago.
2. **Evolução temporal:** como variam as proporções dos três regimes entre jan–ago,
   set–out e nov–dez de 2018, em pontos percentuais? Relatar as três proporções por
   período sem presumir causalidade.
3. **Alertas:** com limiar calibrado em 1% bruto em set–out, quantos alertas são
   produzidos antes e depois do filtro em set–out e nov–dez de 2018, e quantos caem em
   fronteiras? O teste é retrospectivo e o resultado não mede falhas.
4. **Classes conhecidas:** com mapeamento cluster–classe aprendido em jan–ago, qual é
   a concordância com `Load_Type` em nov–dez de 2018, por ARI e F1 macro, e como ela
   se compara à classificação supervisionada e à classe majoritária do treino?
5. **Investigação operacional:** em um piloto ainda sem data definida, que proporção
   dos casos selecionados para triagem recebe parecer e que proporção dos alertas
   revisados é considerada útil? A meta de utilidade e o plano de amostragem devem ser
   acordados antes da avaliação; sem esses dados, a pergunta permanece em aberto.

As quatro primeiras são delimitadas à base histórica; a quinta tem métricas e
população proposta, mas seu prazo e amostragem ainda precisam ser definidos para ser
plenamente SMART. Resultados estão em [Avaliação](../evaluation.md).

## 10. Restrições e riscos

**Orçamento, prazo, aspectos legais, éticos e qualidade dos dados.**

- **Orçamento e prazo:** não foram informados; não há estimativa aprovada de custo,
  prazo de entrega ou custo de operação.
- **Dados e generalização:** um ano e uma instalação não demonstram desempenho em
  outros anos ou plantas; há dependência temporal e possível mudança entre períodos.
- **Avaliação:** EDA e revisão já expuseram o teste histórico. A taxa de alertas é uma
  premissa; sem exemplos rotulados, não é possível medir precisão de falhas.
- **Operação:** o filtro pode suprimir um evento relevante em uma transição e usa a
  leitura seguinte, introduzindo atraso potencial de 15 minutos. Cenários sintéticos
  medem resposta a alterações artificiais, não comprovam detecção correta.
- **Legal e ética:** respeitar a licença CC BY 4.0 e a atribuição da fonte. A base
  pública não autoriza inferir dados pessoais ou atribuir responsabilidade a pessoas;
  não foram estabelecidos requisitos internos específicos da empresa.
- **Interpretação:** nomes como “produção” ou “ocioso capacitivo” são hipóteses
  descritivas; não provam a causa física nem autorizam uma ação automática.

## 11. Ação esperada por grupo

**Que decisão poderá ser tomada a partir de cada resultado?**

| Resultado | Ação proposta | Quem valida ou decide |
| --- | --- | --- |
| Ocioso indutivo | Verificar se corresponde ao padrão de baixa atividade noturna e se o nome é apropriado. | Operação/planta, se disponível. |
| Ocioso capacitivo | Investigar se existe compensação reativa ligada em pausas ou horários específicos. | Operação e responsável elétrico, se disponíveis. |
| Produção | Examinar o perfil de maior consumo e suas diferenças entre períodos. | Analista de energia e operação. |
| Alerta bruto mantido | Priorizar para triagem e registrar parecer; não disparar manutenção automaticamente. | Operação. |
| Alerta suprimido em fronteira | Revisar uma amostra e decidir se o filtro deve permanecer ativo. | Operação. |
| Classe prevista `Load_Type` | Comparar com o rótulo observado para avaliar classificação, especialmente erros entre carga média e máxima. | Equipe de dados; uso operacional depende de aprovação. |

As ações são propostas para orientar uma futura avaliação, não decisões já aprovadas
pela empresa. O [Quadro PBL](pbl-board.md) acompanha as pendências.
