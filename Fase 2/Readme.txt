PosTech - Data Analytics | Fase 2

Repositorio referente a Fase 2 da pos-graduacao em Data Analytics da FIAP/PosTech.

=================================================================
SOBRE O PROJETO
=================================================================

Este projeto usa o dataset WineQT para responder a uma pergunta de negócio objetiva: **o vinho é de alta qualidade?**

A variável `quality` é convertida em um alvo binário:

- `quality >= 7`: classe 1 (alta qualidade)
- `quality < 7`: classe 0

Como a classe positiva é minoritária, a decisão do projeto foi orientada por métricas de equilíbrio e sensibilidade da classe relevante (F1, recall, precision, ROC-AUC e Average Precision), com avaliação final em teste reservado.

## A história analítica do projeto

O trabalho foi estruturado como uma trilha de decisão em sete movimentos:

1. entender o dado e o desbalanceamento da classe positiva (EDA);
2. comparar candidatos supervisionados sob a mesma régua de métricas;
3. usar regressão linear como benchmark de diagnóstico, não como solução final;
4. confirmar generalização com treino/teste em dados não vistos;
5. validar estabilidade com validação cruzada;
6. usar clusterização como leitura complementar de estrutura do dado;
7. calibrar limiar e fechar recomendação operacional no teste reservado.

Esse encadeamento evita decisões por uma única métrica isolada e preserva rastreabilidade entre hipótese, evidência e conclusão.

=================================================================
EQUIPE
=================================================================

- Julia Ayumi Suzuki
- Larissa Nicoli Rodrigues
- Matheus Silva de Jesus
- Paulo Jean Alves da Silva

=================================================================
ARQUIVOS PARA APRESENTACAO
=================================================================

1) Url de git :
   Caminho: https://github.com/Milhousepaulojean/PosTech--DataAnalytics/tree/main/Fase%202


2) Notebook
   Caminho: TechChallenge/Notebook/
   Os notebooks registram a narrativa técnica completa, do diagnóstico à recomendação final:

   - 01_eda.ipynb: contexto inicial do dado, desbalanceamento, correlações e diagnóstico de outliers.
   - 02_modelo_e_validacao.ipynb: comparação de modelos, avaliação de outliers, ajuste de limiar e recomendação final.
   - 03_regressao_linear.ipynb: benchmark linear para validar limitações de hipótese estritamente linear.
   - 04_train_test_split.ipynb: verificação de generalização em teste reservado.
   - 05_validacao_cruzada.ipynb: consistência de desempenho em múltiplas partições.
   - 06_clusterizacao.ipynb: análise não supervisionada como apoio interpretativo.
   - 07_arvore_decisao_pm.ipynb: explicabilidade por árvore e comparação com desempenho global.

3) relatorio_executivo.pdf
   Caminho: TechChallenge/reports/relatorio_executivo.pdf
   Descricao: Relatorio executivo final pronto para entrega


4) Apresentacao com Slides
   Caminho: 
   Descricao: Apresentacao com Slides

5) video youtube
   URL: 
   Descricao: Video para apresentacao