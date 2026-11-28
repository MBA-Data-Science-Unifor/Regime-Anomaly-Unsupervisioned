# Implementação

O dashboard está organizado em abas de visão geral, monitoramento, alertas, modelos,
cenários e artefatos. **Modelos** apresenta a finalidade e os limites do K-Means,
Isolation Forest e experimento supervisionado KNN; apenas o pacote não supervisionado
está disponível para inferência. Em **Cenários**, um dia de validação e valores de
consumo, reativa e fator de potência podem ser escolhidos para testar alterações
sintéticas sem retreinar ou publicar o modelo. A tabela mostra escore, alerta bruto,
fronteira e alerta filtrado. Cenários não substituem rótulos de falha.

A aba **Artefatos** identifica a origem de cada arquivo e compara seu SHA-256 com o
manifesto. Arquivos ausentes, divergentes ou com proveniência conflitante não são
consumidos pelas seções dependentes; quando não há entrada no manifesto, a interface
avisa que a integridade não foi verificada. A preparação vem de `preprocessing.json`
e `prepared_dataset.csv` do notebook 02; métricas, resultados e modelo vêm do notebook
03. O uso de CSV enviado para inferência continua disponível nessa aba.

## Componentes

| Componente | Responsabilidade |
| --- | --- |
| artifacts/notebooks | registro da análise; os notebooks 02–05 ajustam, avaliam e publicam |
| src/regime_anomaly | código reutilizável compartilhado pelos notebooks e pela inferência (`preprocessing`, `modeling`, `artifacts`) |
| artifacts | contrato local de publicação dos artefatos gerados |
| src/app.py | dashboard somente leitura de monitoramento, alertas, modelos e relatórios |
| docs | metodologia, evidências, decisões e limitações |
| tests | verificações de pré-processamento, pacote do modelo, manifesto e traduções |

## Política de artefatos

Dados brutos, conjuntos processados, figuras PNG, tabelas CSV, modelos serializados e
metadados são gerados localmente e ignorados pelo Git. Marcadores dos diretórios
permanecem versionados. `metadata/manifest.json` registra o tamanho, o hash SHA-256, o
identificador UCI, o DOI e a licença do arquivo bruto, o hash SHA-256 de cada artefato
publicado e os passos de reprodução.

O Streamlit não deve treinar nem reescrever artefatos analíticos. Ele permanece utilizável
em modo informativo quando artefatos opcionais estiverem ausentes e recarrega resultados
publicados em `data/processed/analysis_results.csv` por ação explícita do usuário.

O dashboard apresenta resultados históricos como simulação de monitoramento; alertas são
suporte à investigação operacional, não diagnóstico de falha ou previsão de manutenção.

## Execução

    uv sync --locked --group analysis --group docs --group test
    uv run invoke notebooks                 # 01 a 04 em ordem; --start 03_Modeling para retomar
    uv run regime-analysis                  # compara os artefatos com o manifesto
    uv run streamlit run src/app.py
    uv run invoke docs --build --strict
    uv run pytest

O `regime-analysis` termina com status 1 quando um artefato registrado está ausente ou
seu hash difere, de modo que pode proteger uma etapa de implantação.

## Ainda não definido

O monitoramento e o retreinamento dependem da revisão pendente da equipe (consulte
[Situação](status.md)): a taxa de alertas e os nomes dos regimes precisam ser confirmados
antes que limiares de desvio ou um calendário de retreinamento façam sentido.
