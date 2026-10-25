# Memorando de revisão de validação

## Objetivo
Revisar se a comparação de modelos é justa, segura contra leakage e apoiada por métricas adequadas antes de encaminhar a evidência ao PM ou à área de QA/documentação.

## Achados sobre split e leakage
- O conjunto de dados foi dividido em uma ordem segura contra leakage: treino/validação/teste foi criado antes do preprocessamento.
- O conjunto de teste final foi reservado e não foi usado para a seleção do modelo.
- A estratificação foi aplicada à variável alvo, o que é adequado para um problema de classificação binária desbalanceado.
- O preprocessamento foi ajustado apenas sobre os dados de treino; os dados de validação foram transformados com o scaler aprendido.
- A coluna `Id` foi excluída dos preditores, em conformidade com as restrições do projeto.

## Achados sobre preprocessamento e métricas
- O preprocessamento utilizou `StandardScaler` apenas em variáveis numéricas.
- Isso é aceitável para o conjunto atual de features e não vaza informação dos dados de validação ou teste.
- Como a classe positiva é rara, a acurácia isolada é insuficiente. As métricas relevantes são F1, precision, recall, balanced accuracy, ROC-AUC e average precision.
- A comparação escolhida é justa porque todos os modelos foram treinados e validados com os mesmos dados preparados e o mesmo split.

## Resumo da evidência do modelo
- HistGradientBoostingClassifier: F1 = 0,6667, precision = 0,7600, recall = 0,5938, ROC-AUC = 0,9261, average precision = 0,6688
- RandomForestClassifier: F1 = 0,6563, precision = 0,6563, recall = 0,6563, ROC-AUC = 0,9408, average precision = 0,7578
- LogisticRegression: F1 = 0,5545, precision = 0,4058, recall = 0,8750, ROC-AUC = 0,8669, average precision = 0,4762
- Baseline majoritário: F1 = 0,0000; não é um competidor válido para os modelos reais.

## Decisão
Decisão: pronto para revisão do PM com cautela.

Justificativa:
- O fluxo de split e preprocessamento é seguro contra leakage.
- A comparação é reproduzível e baseada apenas em dados de validação.
- A priorização de métricas escolhida é apropriada para o desbalanceamento de classes.
- A conclusão não é final até que o conjunto de teste reservado seja usado para a avaliação final, mas ela já está suficientemente sustentada para avançar para a revisão do stakeholder.

## Próxima ação e owner
- Próximo owner: QA e Documentação Python.
- A área de QA deve confirmar a reprodutibilidade, a organização dos arquivos e a clareza das instruções finais de execução e documentação.
- Após a QA, o PM pode decidir se aprova a recomendação final ou solicita uma revisão do threshold da classe alvo.
