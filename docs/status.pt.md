# Situação do Projeto

| Item | Situação |
| --- | --- |
| Conjunto bruto da indústria siderúrgica | disponível localmente |
| Notebook de EDA | implementado; revisão em andamento |
| Notebook de preparação | 02 (síntese exploratória e protocolo publicado); decisões aguardando aprovação |
| Módulo de pré-processamento | `preprocessing.py` com testes |
| Notebook de modelagem | implementado com protocolo fixado antes dos resultados |
| Modelo selecionado | K-Means, três regimes, apenas variáveis elétricas |
| Detector de anomalias | Isolation Forest, limiar de 1% calibrado na validação |
| Filtro de transição | v1.1: alertas nas fronteiras de regime suprimidos (59 → 7 na validação) |
| Avaliação congelada | concluída em novembro–dezembro |
| Pacote serializado | `final_model.joblib` com `ModelBundle.predict` e testes |
| Manifesto de integridade | `metadata/manifest.json` com SHA-256 por artefato e proveniência dos dados brutos; verificado por `uv run regime-analysis` |
| Reprodução | `uv run invoke notebooks` executa 01–04 em ordem |
| Streamlit | painel de monitoramento (visão geral, monitoramento, alertas, modelos, relatórios) que lê os resultados publicados, mais uma página que executa o modelo em um CSV enviado |
| MkDocs | atualizado até a avaliação |

## Pendências

Os itens 1–3 dependem de pessoas. Cada um está preparado em
[Revisão da equipe](team-review.md) e em `artifacts/notebooks/04_Review.ipynb`.

1. **Aprovação da equipe** das decisões D1–D9 (registro de decisões pronto);
2. **Respostas da equipe da planta** a quatro perguntas sobre os nomes dos regimes e o
   horário do banco de capacitores (evidências prontas);
3. **Triagem pela operação** de 579 alertas em `revisao_alertas_triagem.csv`, começando
   pelos 38 alertas isolados em dois episódios (noites de 15–23 de julho, manhã de 22 de
   maio), e confirmação de que as transições de regime não são de interesse (base do
   filtro v1.1);
4. registrar o histórico de contribuições.

## Resolvido

- **Tratamento de timestamps na EDA.** O notebook 01 agrupa pela data da fonte, que já
  atribui a leitura das 24:00 ao dia que ela encerra (verificado em 100% das linhas
  contra os timestamps corrigidos). A correção cronológica só é necessária onde a ordem
  importa e é aplicada no notebook 02; o notebook 01 agora documenta essa convenção.
- **Lacunas de reprodutibilidade.** O `nbconvert` agora está declarado no grupo
  `analysis`, o `requirements.txt` é exportado do `uv.lock` (antes era um freeze parcial
  em UTF-16 sem Streamlit nem Plotly) e a CI também verifica a formatação.
