# Critérios de Sucesso

## Dados

- documentar os 11 campos, unidades, papéis e domínios observados;
- preservar o CSV bruto sem alterações;
- verificar valores ausentes, duplicatas, tipos, frequência e cobertura temporal;
- tornar a preparação reproduzível e segura contra vazamento.

## Modelagem não supervisionada

- usar exatamente três grupos para a hipótese principal de regimes;
- registrar sementes, pré-processamento, variáveis e parâmetros;
- comparar pelo menos duas geometrias de agrupamento compatíveis;
- avaliar compacidade, separação, estabilidade e comportamento temporal;
- tratar a contaminação e os limiares de anomalia como premissas explícitas.

## Avaliação

- manter `Load_Type` fora das entradas dos modelos; o experimento supervisionado usa
  seus valores como rótulo de treino e a avaliação externa usa-os como referência;
- não usar métricas supervisionadas durante a EDA;
- relatar concordância externa sem usá-la para treinar os agrupamentos e reconhecer
  que o teste histórico não é plenamente independente;
- relatar alertas e limitações; a sensibilidade para falhas requer rótulos ainda ausentes;
- distinguir descobertas exploratórias de conclusões aprovadas.

## Entrega

- manter artefatos gerados ou pesados fora do Git;
- reproduzir os artefatos a partir dos notebooks (`uv run invoke notebooks`) e
  verificá-los com `uv run regime-analysis`;
- construir o MkDocs em modo estrito;
- manter o Streamlit somente leitura em relação ao treinamento;
- manter testes aprovados e um manifesto de integridade antes da publicação final.

Os valores da regra de seleção e as propostas de sucesso de negócio estão no
[Canvas PBL](pbl/problem-canvas.md). As metas de negócio e de utilidade dos alertas
ainda precisam de aprovação operacional.
