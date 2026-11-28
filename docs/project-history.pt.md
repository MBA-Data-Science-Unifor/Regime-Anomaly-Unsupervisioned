# Histórico de percepções e decisões

Este registro reúne, em ordem lógica, as principais percepções das análises e revisões
do projeto. É uma reconstrução retrospectiva: a sequência descreve a evolução do
trabalho, sem afirmar datas ou uma cronologia de decisões que não foram registradas.
Os números correspondem aos artefatos disponíveis na revisão e podem mudar em uma
nova execução. Para a situação atual, consulte [Avaliação](evaluation.md) e
[Revisão da equipe](team-review.md).

## 1. Entendimento dos dados e exploração

- A base contém 35.040 leituras de 15 minutos de 2018. A leitura registrada como
  `00:00` encerra o dia indicado no arquivo; sua correção para a meia-noite seguinte
  torna a série cronológica e sustenta a divisão temporal.
- Consumo e CO₂ têm associação quase linear; por isso, CO₂ foi retirado das entradas
  principais para reduzir redundância, permanecendo disponível para descrição.
- Consumo e variáveis elétricas mostram assimetria e ciclos de calendário. Valores
  extremos foram preservados por serem relevantes para a investigação de anomalias.
- A EDA examinou o ano inteiro. Assim, embora novembro–dezembro tenha sido reservado
  na modelagem, esse período não constitui uma avaliação plenamente independente.

## 2. Preparação e definição dos regimes

- Foi adotada a divisão temporal janeiro–agosto para treino, setembro–outubro para
  validação e novembro–dezembro para teste. Os transformadores e modelos são ajustados
  no treino; o limiar de anomalias é calibrado na validação.
- A hipótese de três regimes usa a cardinalidade de `Load_Type`: os modelos são não
  supervisionados, mas a escolha de três grupos incorpora informação externa. A
  inspeção do rótulo no treino também apoiou a exclusão do calendário das entradas
  principais de regime.
- K-Means com variáveis elétricas foi selecionado entre os candidatos elegíveis: na
  validação, apresentou silhueta 0,823 e ARI médio de bootstrap 0,999. Esses indicadores
  descrevem separação e estabilidade, não comprovam estados operacionais reais.
- Os perfis receberam os nomes **ocioso indutivo**, **ocioso capacitivo** e
  **produção**. A hipótese de compensação reativa acionada por horário e os nomes
  ainda precisam de confirmação com a planta.

## 3. Anomalias e filtro de transição

- O Isolation Forest recebeu um limiar correspondente ao percentil 99 dos escores da
  validação. A taxa de 1% é uma premissa de operação, não uma estimativa da frequência
  real de falhas; não há rótulos de falha para medir precisão ou sensibilidade.
- Uma grande parcela dos alertas coincidiu com fronteiras entre regimes. Na validação,
  52 dos 59 alertas brutos estavam em fronteira, uma concentração cerca de 9,5 vezes
  maior que a proporção dessas leituras. Isso motivou o filtro da versão v1.1.
- O filtro publicado reduziu os alertas de 59 para 7 na validação e de 49 para 5 no
  teste. Também pode suprimir eventos relevantes; os escores e alertas brutos foram
  mantidos, e a decisão de manter o filtro aguarda avaliação operacional.
- A regra do filtro foi formulada após a revisão de evidências que incluíam o teste;
  seus números não são um teste cego independente. A recorrência calculada sobre o
  ano completo é retrospectiva: em uso contínuo deve considerar apenas o passado.

## 4. Revisão da qualidade e concordância externa

- A silhueta global caiu de 0,823 na validação para 0,768 no teste. Na análise por
  regime, produção apresentou as menores médias: 0,670 e 0,662, respectivamente.
- Para avaliar concordância com `Load_Type`, cada cluster foi associado à classe mais
  frequente no treino. No teste, a acurácia foi 59,6%, a acurácia balanceada 55,9% e
  o F1 macro 54,0%; a referência da classe majoritária atingiu 53,1%. A sensibilidade
  de `Medium_Load` foi 33,4%.
- As curvas ROC usam proporções de classes do treino por cluster, não probabilidades
  calibradas. Essas métricas avaliam concordância com `Load_Type`; não avaliam a
  capacidade de detectar falhas. Os resultados detalhados e suas fontes estão em
  [Avaliação](evaluation.md).

## 5. Pontos em aberto

1. Validar com a operação os nomes dos regimes, os episódios destacados e o interesse
   de alertar durante transições.
2. Obter pareceres sobre alertas e também sobre uma amostra de leituras não alertadas
   para permitir uma avaliação de falhas mais abrangente.
3. Avaliar o modelo e o filtro em um período posterior não usado para explorá-los ou
   defini-los, preservando decisões e limiares antes da consulta aos resultados.
4. Para uso em tempo real, definir o tratamento da leitura seguinte necessária à
   identificação de fronteiras e calcular recorrência sem usar observações futuras.

## Equipe e responsabilidades

| Integrante | Função no projeto | Responsabilidades informadas |
| --- | --- | --- |
| Alexandre Franco | Analista de Dados e Modelagem | Análise dos dados e aplicação de modelos, incluindo técnicas não supervisionadas. |
| Rodrigo Franco | Engenheiro de Dados | Engenharia de dados. |
| Caio Cunha Franco | Engenheiro de IA | Engenharia de inteligência artificial. |

As funções descrevem as responsabilidades informadas pela equipe e podem ser detalhadas
conforme as contribuições forem registradas.
