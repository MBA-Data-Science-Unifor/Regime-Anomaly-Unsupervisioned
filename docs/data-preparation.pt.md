# Preparação dos Dados

A preparação está em dois notebooks que compartilham
`src/regime_anomaly/preprocessing.py`:

- `artifacts/notebooks/02_preprocessing.ipynb` — comparação exploratória de
  configurações de variáveis (divisão temporal 80/20, one-hot de `Day_of_week`, PCA
  opcional);
- `artifacts/notebooks/02b_Preprocessing_Protocol.ipynb` — a preparação usada pelo
  modelo publicado (notebooks 03–05), descrita abaixo.

!!! warning "Decisões propostas"
    As escolhas abaixo são propostas baseadas em evidências que aguardam aprovação da
    equipe. Os dois notebooks chegam à mesma conclusão sobre as entradas de calendário:
    apenas as variáveis elétricas produzem a maior silhueta (0,636 no notebook 02; 0,82
    na validação no 02b).

## Pipeline

1. **Correção dos timestamps.** As leituras são registradas no fim do seu intervalo de
   15 minutos. A leitura que encerra cada dia (24:00) é armazenada após 23:45 com a
   mesma data de calendário e `NSM = 0`, de modo que uma interpretação ingênua a coloca
   24 horas antes (365 saltos para trás). Essas linhas passam para a meia-noite seguinte;
   a série se torna uma grade contínua de 15 minutos de 2018-01-01 00:15 a 2019-01-01
   00:00.
2. **Validação estrutural.** A execução é interrompida diante de nulos, timestamps
   duplicados, lacunas na frequência, energia negativa, fator de potência fora de 0–100
   ou categorias de calendário desconhecidas.
3. **Variáveis de calendário (locais à linha).** Seno/cosseno da hora do dia (a partir
   de `NSM`) e do dia da semana, mais um indicador de fim de semana.
4. **Divisão cronológica.** Treino de janeiro a agosto (23.328 linhas), validação de
   setembro a outubro (5.856) e teste de novembro a dezembro (5.856). Uma leitura
   registrada exatamente em uma fronteira encerra o período anterior e permanece desse
   lado. O período de teste fica congelado até a avaliação final.
5. **Transformações, ajustadas apenas no treino.** `log1p` nas variáveis de energia,
   `log1p(100 − PF)` nos fatores de potência e, em seguida, `StandardScaler`.

## Conjuntos de variáveis

| Conjunto | Entradas | Finalidade |
| --- | --- | --- |
| `regime` | 3 variáveis de energia + 2 de fator de potência | agrupamento principal dos regimes |
| `regime_with_calendar` | `regime` + 5 variáveis de calendário | análise de sensibilidade |
| `anomaly` | `regime` + hora do dia + indicador de fim de semana | detecção contextual de anomalias |

## Principais evidências

- **`Load_Type` se comporta como uma tabela horária de tarifa.** De 00:00 a 08:59 ele é
  sempre `Light_Load`, e uma regra de maioria sobre hora do dia, situação da semana e mês
  reproduz cerca de 92% dos rótulos de treino (um ajuste dentro da amostra, sobre cerca de 1.500 faixas de calendário). Entradas de calendário permitiriam que os
  grupos reconstruíssem a tabela tarifária; por isso, o conjunto principal de regimes as
  exclui e usa o calendário apenas para descrever os grupos.
- **O CO2 é excluído** de todos os conjuntos de variáveis: Pearson ≈ 0,99 com o consumo,
  apenas oito valores distintos e 58% de zeros. Ele continua disponível para a
  caracterização dos perfis.
- **Os extremos são mantidos.** Encontrar observações incomuns é um objetivo do projeto;
  recortá-los apagaria esse sinal.
- **Existe desvio.** O consumo mediano é cerca de 23% menor na validação do que no
  treino, de modo que a validação também mede a robustez temporal.

A comparação de escores usada durante esta seleção experimental está publicada em
[Descobertas iniciais](initial-findings.md) e pode ser regenerada a partir da saída
armazenada do notebook com `python scripts/generate_docs_figures.py`.

## Limite contra vazamento

`Load_Type` nunca é uma variável (`assert_no_label` protege todos os conjuntos de
variáveis). Ele foi inspecionado apenas no período de treino, para entender seu
significado, e fora isso fica reservado para a avaliação externa. Os transformadores
ajustados não são serializados durante a preparação; o notebook 03 os reajusta no treino
e os armazena junto com o modelo final.

## Saídas (regeneradas localmente, não versionadas)

- `artifacts/data/processed/prepared_dataset.csv`
- `artifacts/metadata/preprocessing.json` (SHA-256 do arquivo bruto, fronteiras,
  conjuntos de variáveis, relatório de qualidade, versões das bibliotecas)
- `artifacts/tables/preprocessamento_*.csv` e as figuras `21`–`24` em `artifacts/images/`

## Decisões ainda em aberto

- o kVarh adiantado e o fator de potência adiantado mantêm grande massa no seu limite
  (0 / 100%); testar um indicador binário de "no limite";
- redundância do par kVarh adiantado × fator de potência adiantado (Spearman ≈ −0,97);
- calibração do limiar de anomalia na validação em vez de uma contaminação fixa de 2%.
