# Nota de decisão do PM

## Objetivo
Confirmar se a recomendação do modelo continua estável após a revisão final dos notebooks, das métricas de validação e do teste reservado, e decidir o que deve entrar no relatório executivo final.

## Status atual
- EDA concluída e documentada.
- Preprocessamento concluído com split seguro contra leakage e escalonamento aplicado somente sobre treino.
- Comparação de modelos concluída com foco em métricas adequadas à classe minoritária.
- Testes de regressão linear, split, validação cruzada, clusterização e árvore de decisão concluídos.
- A decisão final foi reavaliada com o conjunto de teste reservado e a recomendação foi ajustada no detalhe, sem mudar a direção estratégica.

## Evidências e riscos
- Na validação interna, HistGradientBoostingClassifier foi ligeiramente melhor em F1 e precisão.
- No teste reservado, RandomForest balanced ficou melhor em recall e F1, enquanto HistGradientBoostingClassifier continuou forte em precisão.
- Regressão linear e clusterização não são empregadas como modelo principal e não alteram a recomendação final.
- O problema é desbalanceado e a acurácia isolada é insuficiente para decidir o melhor modelo.
- A escolha final depende do eixo de negócio: recall/F1 ou precisão.

## Decisão
Decisão: proceed, com ajuste na recomendação final.

Justificativa:
- A direção estratégica permanece a mesma: modelos baseados em árvores e ensembles são os mais adequados para o problema.
- O ajuste final é que, no teste reservado, o RandomForest balanced se mostrou melhor como modelo principal.
- HistGradientBoostingClassifier continua como alternativa forte, principalmente se a organização priorizar precisão.
- Regressão linear, clusterização e árvore de decisão continuam como ferramentas diagnósticas ou interpretativas, não como solução principal.

## Próximo owner e ação
- Próximo owner: PM + líder técnico + stakeholder.
- Ação: consolidar o relatório executivo final, explicitando que a recomendação principal foi ajustada para RandomForest balanced, com HistGradientBoostingClassifier como alternativa forte e árvore de decisão como suporte interpretativo.
