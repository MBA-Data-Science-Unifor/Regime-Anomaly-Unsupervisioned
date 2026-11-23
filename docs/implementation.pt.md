# Implementação

## Componentes

| Componente | Responsabilidade |
| --- | --- |
| artifacts/notebooks | registros de investigação e experimentos |
| src/regime_anomaly | código reutilizável aprovado |
| artifacts | contrato local de publicação dos artefatos gerados |
| src/app.py | apresentação somente leitura e inferência futura |
| docs | metodologia, evidências, decisões e limitações |
| tests | validação estrutural e de inferência futura |

## Política de artefatos

Dados brutos, conjuntos processados, figuras PNG, tabelas CSV, modelos serializados e
metadados são gerados localmente e ignorados pelo Git. Marcadores dos diretórios
permanecem versionados. Um futuro manifesto fornecerá hashes e instruções de reprodução.

O Streamlit não deve treinar nem reescrever artefatos analíticos. Ele deve permanecer
utilizável em modo informativo quando artefatos opcionais estiverem ausentes.

## Execução

    uv run streamlit run src/app.py
    uv run --group docs invoke docs --build --strict
    uv run --group test pytest

O plano de implantação, monitoramento e retreinamento será definido somente após a
avaliação final.
