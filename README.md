# RT-IoT2022 — Regimes e Anomalias

Projeto em desenvolvimento para detecção não supervisionada de regimes e anomalias
em tráfego IoT com a base RT-IoT2022. A apresentação dos resultados é feita
exclusivamente em Streamlit.

## Equipe

- Alexandre Franco
- Caio Cunha Franco
- Rodrigo Franco

O histórico de alterações e a descrição das contribuições individuais serão
adicionados futuramente.

## Estado atual

O repositório contém a estrutura inicial do projeto. A análise, a escolha do modelo,
as métricas e os resultados finais ainda não estão concluídos.

Os três notebooks do projeto estão em `artifacts/notebooks/`:

1. `01_EDA.ipynb` — análise exploratória;
2. `02_preprocessing.ipynb` — preparação e pré-processamento;
3. `03_Modeling.ipynb` — modelagem, ainda em desenvolvimento.

## Estrutura

```text
artifacts/
├── data/
│   ├── raw/RT_IOT2022       # base local
│   └── processed/            # dados processados futuros
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_preprocessing.ipynb
│   └── 03_Modeling.ipynb
├── tables/                   # tabelas futuras
├── images/                   # imagens futuras
├── models/                   # modelo final futuro
└── metadata/                 # métricas e manifesto futuros
docs/
├── index.md                  # visão geral do MkDocs
├── methodology.md            # metodologia do projeto
├── business-understanding.md # entendimento do problema
├── success-criteria.md       # critérios de sucesso
├── data-source.md            # fonte dos dados
├── data-understanding.md     # entendimento dos dados
├── exploratory-analysis.md   # roteiro da EDA
├── data-preparation.md       # preparação planejada
├── modeling.md               # modelagem planejada
├── evaluation.md             # protocolo de avaliação
├── implementation.md         # arquitetura de implementação
├── project-analysis.md       # estrutura planejada
├── pbl/                      # canvas e quadro PBL
└── status.md                 # estado atual
src/
├── app.py                    # aplicação Streamlit
└── regime_anomaly/
    ├── locales/              # traduções pt-BR e en da interface
    └── i18n.py               # carregamento das traduções
tests/                        # testes estruturais
mkdocs.yml                    # configuração da documentação
```

O Streamlit será responsável por ler tabelas, imagens, métricas e o modelo publicados
em `artifacts/`. Ele não deve executar treinamento.

## Idiomas

A interface Streamlit usa português brasileiro (`pt-BR`) por padrão e permite a
troca para inglês. Os textos ficam separados do código em
`src/regime_anomaly/locales/`.

A documentação em `docs/` permanece escrita em inglês. Apenas os controles do tema
MkDocs são apresentados em português brasileiro.

## Ambiente

Python 3.12 ou superior e [uv](https://docs.astral.sh/uv/) são necessários.

```bash
uv sync --locked
```

As dependências devem ser adicionadas pelo terminal, sem editar o lockfile manualmente:

```bash
uv add nome-da-biblioteca
uv add --group dev nome-da-biblioteca-de-desenvolvimento
```

Os grupos opcionais definidos em `pyproject.toml` separam o ambiente de análise
(`analysis`), documentação (`docs`), testes (`test`) e desenvolvimento (`dev`).

## Execução

Aplicação Streamlit:

```bash
uv run streamlit run src/app.py
```

Preparação dos diretórios e exibição do contrato de artefatos, sem treinamento:

```bash
uv run regime-analysis
```

Documentação local:

```bash
uv run --group docs invoke docs
```

Build estrito do MkDocs:

```bash
uv run --group docs invoke docs --build --strict
```

Testes e lint:

```bash
uv run --group test pytest
uv run --group dev ruff check src tests tasks.py
```

## Qualidade e integração contínua

O workflow `.github/workflows/ci.yml` executa automaticamente em pushes, pull
requests e por acionamento manual. Ele usa o `uv.lock` para validar lint, tipos,
testes com cobertura, documentação e o pacote Python.

Para reproduzir localmente as mesmas verificações:

```bash
uv sync --locked --group dev --group test --group docs
uv run ruff check src tests tasks.py
uv run mypy
uv run pytest --cov=regime_anomaly --cov-report=term-missing
uv run invoke docs --build --strict
uv build
```
