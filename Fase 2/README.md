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
    │   └── model_validation_metrics.json
    └── src/
        ├── data_preparation.py
        └── model_comparison.py
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

### Resultados e relatório

- `TechChallenge/results/model_validation_metrics.json`: métricas dos modelos na validação.
- `TechChallenge/results/final_test_evaluation.json`: avaliação final no conjunto de teste.
- `TechChallenge/reports/relatorio_executivo.py`: script de geração do relatório.
- `TechChallenge/reports/relatorio_executivo.html`: relatório executivo exportado.
- `TechChallenge/reports/figures/`: imagens e gráficos da análise.

## Como executar

No terminal, a partir da pasta `Fase 2/`, crie e ative um ambiente virtual (opcional, mas recomendado), instale as dependências e execute os scripts:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r TechChallenge/requirements.txt
python TechChallenge/src/data_preparation.py
python TechChallenge/src/model_comparison.py
```

Os comandos acima assumem que os scripts aceitam execução direta e encontram os dados usando caminhos relativos ao projeto. Se necessário, execute-os a partir de `TechChallenge/` ou consulte as configurações de caminho nos próprios scripts.

## Observações

- O problema é tratado como classificação binária; a classe positiva representa vinhos com `quality >= 7`.
- Como as classes podem estar desbalanceadas, avalie também precisão, recall, F1 e ROC-AUC, sem depender apenas da acurácia.

## Conclusão

Este repositório reúne a análise exploratória, a preparação dos dados, a comparação de modelos e a avaliação final da classificação do WineQT. A organização facilita a leitura, o estudo e a reprodução das etapas do projeto.