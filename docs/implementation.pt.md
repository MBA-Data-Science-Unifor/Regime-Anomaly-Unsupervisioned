# Implementação

## Componentes

| Componente | Responsabilidade |
| --- | --- |
| artifacts/notebooks | registros de investigação e experimentos |
| src/regime_anomaly | código reutilizável aprovado |
| artifacts | contrato local de publicação dos artefatos gerados |
| src/app.py | dashboard somente leitura de monitoramento, alertas, modelos e relatórios |
| docs | metodologia, evidências, decisões e limitações |
| tests | validação estrutural e de inferência futura |

## Política de artefatos

Dados brutos, conjuntos processados, figuras PNG, tabelas CSV, modelos serializados e
metadados são gerados localmente e ignorados pelo Git. Marcadores dos diretórios
permanecem versionados. Um futuro manifesto fornecerá hashes e instruções de reprodução.

O Streamlit não deve treinar nem reescrever artefatos analíticos. Ele permanece utilizável
em modo informativo quando artefatos opcionais estiverem ausentes e recarrega resultados
publicados em `data/processed/analysis_results.csv` por ação explícita do usuário.

O dashboard apresenta resultados históricos como simulação de monitoramento; alertas são
suporte à investigação operacional, não diagnóstico de falha ou previsão de manutenção.

## Execução

    uv run streamlit run src/app.py
    uv run --group docs invoke docs --build --strict
    uv run --group test pytest

O plano de implantação, monitoramento e retreinamento será definido somente após a
avaliação final.
