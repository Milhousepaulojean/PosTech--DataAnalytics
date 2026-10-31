# PosTech — Data Analytics | Fase 2

Repositório referente à Fase 2 da pós-graduação em Data Analytics da FIAP/PosTech.

## Navegação rápida

- Repositório no GitHub: [Fase 2](https://github.com/Milhousepaulojean/PosTech--DataAnalytics/tree/main/Fase%202)
- Pasta principal do projeto: [`TechChallenge`](TechChallenge/)

## Objetivo

O projeto utiliza o dataset WineQT para responder a uma pergunta de classificação: **o vinho é de alta qualidade?**

A variável `quality` é convertida em um alvo binário:

- `quality >= 7`: classe 1 (alta qualidade)
- `quality < 7`: classe 0

O fluxo de análise inclui a exploração dos dados, a preparação das amostras de treino, validação e teste, o preprocessamento, a comparação de modelos e a avaliação final em dados não vistos.

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

Os notebooks documentam a exploração e os experimentos:

- `01_eda.ipynb`: análise exploratória dos dados.
- `02_modelo_e_validacao.ipynb`: comparação e validação de modelos.
- `03_regressao_linear.ipynb`: benchmark com regressão linear.
- `04_train_test_split.ipynb`: estudo da divisão entre treino e teste.
- `05_validacao_cruzada.ipynb`: avaliação por validação cruzada.
- `06_clusterizacao.ipynb`: análise de clusters.
- `07_arvore_decisao_pm.ipynb`: árvore de decisão e interpretação do modelo.

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

## Ordem recomendada de leitura dos resultados

1. `TechChallenge/results/model_validation_metrics.json`.
2. `TechChallenge/results/outlier_cv_experiment.json`.
3. `TechChallenge/results/threshold_cv_experiment.json`.
4. `TechChallenge/results/threshold_test_evaluation.json`.
5. `TechChallenge/reports/relatorio_executivo.html` ou `TechChallenge/reports/relatorio_executivo.pdf`.

## Observações

- O problema é tratado como classificação binária; a classe positiva representa vinhos com `quality >= 7`.
- Como as classes estão desbalanceadas, avalie também precisão, recall, F1, ROC-AUC e Average Precision, sem depender apenas da acurácia.
- A calibração de limiar altera o equilíbrio entre recall e precision: limiar menor tende a aumentar recall e reduzir precision.

## Conclusão

Este repositório reúne a análise exploratória, a preparação dos dados, a comparação de modelos e a avaliação final da classificação do WineQT. A organização facilita a leitura, o estudo e a reprodução das etapas do projeto.