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

- manter `Load_Type` fora das variáveis de treinamento;
- não usar métricas supervisionadas durante a EDA;
- reservar medidas de concordância externa para o protocolo de avaliação congelado;
- relatar casos de falha, sensibilidade e limitações;
- distinguir descobertas exploratórias de conclusões aprovadas.

## Entrega

- manter artefatos gerados ou pesados fora do Git;
- reproduzir os artefatos a partir dos notebooks (`uv run invoke notebooks`) e
  verificá-los com `uv run regime-analysis`;
- construir o MkDocs em modo estrito;
- manter o Streamlit somente leitura em relação ao treinamento;
- manter testes aprovados e um manifesto de integridade antes da publicação final.
