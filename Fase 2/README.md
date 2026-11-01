# PosTech — Data Analytics | Fase 2

Repositório referente à Fase 2 da pós-graduação em Data Analytics da FIAP/PosTech.

## Navegação rápida

- Repositório no GitHub: [Fase 2](https://github.com/Milhousepaulojean/PosTech--DataAnalytics/tree/main/Fase%202)
- Pasta principal do projeto: [`TechChallenge`](TechChallenge/)

## Objetivo

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

## Estrutura do projeto

```text
Fase 2/
├── README.md
└── TechChallenge/
    ├── requirements.txt
    ├── data/
    │   ├── WineQT.csv
    │   └── prepared/
    │       ├── train_prepared.csv
    │       ├── validation_prepared.csv
    │       └── test_prepared.csv
    ├── notebooks/
    │   ├── 01_eda.ipynb
    │   ├── 02_modelo_e_validacao.ipynb
    │   ├── 03_regressao_linear.ipynb
    │   ├── 04_train_test_split.ipynb
    │   ├── 05_validacao_cruzada.ipynb
    │   ├── 06_clusterizacao.ipynb
    │   └── 07_arvore_decisao_pm.ipynb
    ├── reports/
    │   ├── relatorio_executivo.html
    │   ├── relatorio_executivo.py
    │   └── figures/
    ├── results/
    │   ├── final_test_evaluation.json
    │   ├── model_validation_metrics.json
    │   ├── outlier_cv_experiment.json
    │   ├── threshold_cv_experiment.json
    │   └── threshold_test_evaluation.json
    └── src/
        ├── data_preparation.py
        ├── model_comparison.py
        ├── outlier_cv_experiment.py
        ├── threshold_cv_experiment.py
        └── final_threshold_evaluation.py
```

## Componentes

### Dados

`TechChallenge/data/WineQT.csv` contém o dataset original. A pasta `TechChallenge/data/prepared/` reúne os arquivos preparados para treino, validação e teste.

### Notebooks

Os notebooks registram a narrativa técnica completa, do diagnóstico à recomendação final:

- `01_eda.ipynb`: contexto inicial do dado, desbalanceamento, correlações e diagnóstico de outliers.
- `02_modelo_e_validacao.ipynb`: comparação de modelos, avaliação de outliers, ajuste de limiar e recomendação final.
- `03_regressao_linear.ipynb`: benchmark linear para validar limitações de hipótese estritamente linear.
- `04_train_test_split.ipynb`: verificação de generalização em teste reservado.
- `05_validacao_cruzada.ipynb`: consistência de desempenho em múltiplas partições.
- `06_clusterizacao.ipynb`: análise não supervisionada como apoio interpretativo.
- `07_arvore_decisao_pm.ipynb`: explicabilidade por árvore e comparação com desempenho global.

### Scripts

`TechChallenge/src/data_preparation.py` carrega o dataset, cria a variável alvo, divide os dados, normaliza as features e salva os arquivos preparados em `data/prepared/`.

`TechChallenge/src/model_comparison.py` carrega os dados preparados, treina e compara modelos, calcula métricas (acurácia, precisão, recall, F1, ROC-AUC e PR-AUC) e salva os resultados em JSON na pasta `results/`.

`TechChallenge/src/outlier_cv_experiment.py` compara estratégias de tratamento de outliers com validação cruzada estratificada.

`TechChallenge/src/threshold_cv_experiment.py` calibra o limiar de decisão da classe positiva com probabilidades out-of-fold em validação cruzada.

`TechChallenge/src/final_threshold_evaluation.py` aplica os limiares candidatos no teste reservado para fechar a recomendação operacional final.

### Resultados e relatório

- `TechChallenge/results/model_validation_metrics.json`: métricas dos modelos na validação.
- `TechChallenge/results/final_test_evaluation.json`: avaliação final no conjunto de teste.
- `TechChallenge/results/outlier_cv_experiment.json`: comparação de estratégias de outliers na validação cruzada.
- `TechChallenge/results/threshold_cv_experiment.json`: comparação de limiares na validação cruzada.
- `TechChallenge/results/threshold_test_evaluation.json`: impacto dos limiares no teste reservado.
- `TechChallenge/reports/relatorio_executivo.py`: script de geração do relatório.
- `TechChallenge/reports/relatorio_executivo.html`: relatório executivo exportado.
- `TechChallenge/reports/figures/`: imagens e gráficos da análise.

## Como executar

No terminal, a partir da pasta `Fase 2/`, crie e ative um ambiente virtual (opcional, mas recomendado), instale as dependências e execute as etapas abaixo.

### 1) Ambiente e dependências

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r TechChallenge/requirements.txt
```

### 2) Preparação de dados e comparação base de modelos

```bash
python TechChallenge/src/data_preparation.py
python TechChallenge/src/model_comparison.py
```

### 3) Etapa 2: validação experimental de outliers

```bash
python TechChallenge/src/outlier_cv_experiment.py
```

### 4) Etapa 3: calibração de limiar por validação cruzada

```bash
python TechChallenge/src/threshold_cv_experiment.py
```

### 5) Reavaliação no teste reservado com limiares candidatos

```bash
python TechChallenge/src/final_threshold_evaluation.py
```

### 6) Geração do relatório executivo (HTML e PDF)

```bash
python TechChallenge/reports/relatorio_executivo.py
```

Os scripts usam a regra de alvo `quality >= 7` e preservam o teste reservado para a avaliação final.

## Como ler os resultados (sequência recomendada)

Use esta ordem para acompanhar a história de decisão do projeto:

1. desempenho-base na validação: `TechChallenge/results/model_validation_metrics.json`;
2. impacto de estratégias de outliers: `TechChallenge/results/outlier_cv_experiment.json`;
3. efeito da calibração de limiar na validação cruzada: `TechChallenge/results/threshold_cv_experiment.json`;
4. verificação dos limiares no teste reservado: `TechChallenge/results/threshold_test_evaluation.json`;
5. consolidação executiva com interpretação integrada: `TechChallenge/reports/relatorio_executivo.html` ou `TechChallenge/reports/relatorio_executivo.pdf`.

## Observações

- O problema é tratado como classificação binária; a classe positiva representa vinhos com `quality >= 7`.
- Como as classes estão desbalanceadas, avalie também precisão, recall, F1, ROC-AUC e Average Precision, sem depender apenas da acurácia.
- A calibração de limiar altera o equilíbrio entre recall e precision: limiar menor tende a aumentar recall e reduzir precision.

## Conclusão

Este repositório organiza, de forma reproduzível, toda a jornada analítica do WineQT: da leitura exploratória até a decisão operacional de modelo e limiar. O resultado final não é apenas um ranking de métricas, mas uma recomendação técnica rastreável, orientada ao problema de classe desbalanceada e validada em teste reservado.