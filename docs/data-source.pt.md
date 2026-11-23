# Fonte dos Dados

## Conjunto de dados

O projeto usa o conjunto **Steel Industry Energy Consumption**, publicado pelo
[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption).

Caminho local:

    artifacts/data/raw/Steel_industry_data.csv

O projeto nunca baixa nem edita automaticamente o arquivo bruto. As saídas derivadas
ficam em `artifacts/data/processed`.

## Proveniência

As medições são da DAEWOO Steel Co. Ltd, em Gwangyang, Coreia do Sul. O registro da UCI
informa 35.040 instâncias, ausência de valores faltantes, variáveis reais e categóricas e
licença CC BY 4.0. A referência do conjunto é:

Sathishkumar V E, Changsun Shin e Yongyun Cho (2021), *Steel Industry Energy
Consumption*, UCI Machine Learning Repository, DOI 10.24432/C52G8C.

## Granularidade das medições

Cada linha representa uma observação de 15 minutos durante 2018. Os campos abrangem
consumo de energia ativa, energia reativa atrasada e adiantada, CO2, fatores de potência,
segundos desde a meia-noite, contexto de dia útil/fim de semana, dia da semana e tipo de
carga.

Um futuro manifesto deve registrar data de obtenção, tamanho em bytes, hash SHA-256,
identificador UCI, DOI e licença.
