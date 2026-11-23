# Metodologia

O projeto segue o CRISP-DM com separação explícita entre exploração, desenvolvimento de
modelos não supervisionados e avaliação externa posterior.

## Formulação do problema

O conjunto de dados contém três valores de `Load_Type`. Essa quantidade define uma
hipótese estrutural de três regimes operacionais. As identidades das classes não são
usadas para ajustar o pré-processamento, agrupamento, projeções ou detecção de anomalias.

## Fases atuais

1. **Entendimento do negócio:** definir a questão operacional e seus limites.
2. **Entendimento dos dados:** documentar fonte, granularidade, campos, qualidade e
   cobertura temporal.
3. **EDA:** inspecionar distribuições, padrões temporais, correlações, projeções e
   baselines não supervisionados.
4. **Preparação:** criar um pipeline de variáveis reutilizável e seguro contra vazamento.
5. **Modelagem:** comparar métodos candidatos sob um protocolo congelado.
6. **Avaliação:** avaliar geometria, estabilidade, robustez temporal e, somente depois,
   a concordância opcional com categorias externas.
7. **Publicação:** gravar os artefatos aprovados e expô-los como somente leitura.

## Técnicas usadas na EDA

- histogramas de Freedman–Diaconis e diagnósticos de IQR para distribuições;
- Pearson e Spearman para associações lineares e monotônicas;
- perfis de calendário para estruturas intradiária e semanal;
- PCA para uma projeção global interpretável;
- t-SNE apenas para visualização de vizinhanças locais;
- K-Means com K fixado em três como baseline de centroides;
- GMM com três componentes como contraparte probabilística;
- Isolation Forest como baseline exploratório de anomalias.

Cotovelo, silhueta, AIC e BIC são diagnósticos. Eles não substituem a definição do
problema com três regimes.

## Técnicas adiadas

Métodos baseados em densidade, hierárquicos, espectrais, de medóides, de representação
neural e métodos alternativos de anomalia estão documentados no notebook de EDA com seu
uso pretendido, limitações e condições de reconsideração. Estimadores supervisionados e
métricas baseadas em rótulos são deliberadamente excluídos desta fase.

## Reprodutibilidade e publicação

Sementes, transformações, parâmetros e premissas devem ser registrados. Os notebooks
são o registro da investigação; a lógica reutilizável aprovada é movida para
`src/regime_anomaly`. Dados brutos, figuras, tabelas, modelos e arquivos derivados
grandes são regenerados localmente e excluídos do Git.
