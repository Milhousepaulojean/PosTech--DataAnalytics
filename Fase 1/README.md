# PosTech — Data Analytics | Fase 1

Repositório referente à **Fase 1** da pós-graduação em Data Analytics da FIAP/PosTech.

---

## Sobre o projeto

**Pergunta norteadora:** Como a eficiência logística impacta o faturamento dos e-commerces brasileiros?

O projeto analisa o **Brazilian E-Commerce Public Dataset by Olist** — uma base pública com mais de 100 mil pedidos reais do comércio eletrônico brasileiro — e responde essa pergunta por meio de uma análise exploratória estruturada, culminando em um relatório executivo com recomendações de negócio.

A análise investiga:

- a associação entre **atraso na entrega** e a **satisfação dos clientes** (nota de avaliação);
- a **receita associada ao risco operacional** (pedidos atrasados com nota ≤ 2);
- os **estados** com maior exposição financeira;
- o **perfil** dos clientes afetados (novos vs. recorrentes);
- a **evolução mensal** do risco ao longo do tempo;
- a **recompra exploratória** após a primeira experiência.

> Os resultados são descritivos e associativos. Correlação não prova causalidade.

---

## Equipe

| Nome |
|---|
| Julia Ayumi Suzuki |
| Pâmela Cristina da Silva |
| Larissa Nicoli Rodrigues |
| Matheus Silva de Jesus |
| Paulo Jean Alves da Silva |

---

<!-- ## Estrutura de arquivos

```
Fase 1/
├── README.md                          ← este arquivo
└── TechChallenge/
    ├── POSTECH - [DTAT] - Tech Challenge - Fase 1.pdf   ← enunciado oficial
    ├── Notebook.ipynb                 ← análise exploratória principal
    ├── relatorio_executivo.py         ← script que gera o relatório HTML/PDF
    ├── database/                      ← datasets da Olist (CSV)
    │   ├── olist_orders_dataset.csv
    │   ├── olist_order_payments_dataset.csv
    │   ├── olist_order_reviews_dataset.csv
    │   ├── olist_order_items_dataset.csv
    │   ├── olist_customers_dataset.csv
    │   ├── olist_sellers_dataset.csv
    │   ├── olist_products_dataset.csv
    │   ├── olist_geolocation_dataset.csv
    │   └── product_category_name_translation.csv
    └── relatorios/
        └── relatorio_executivo.pdf    ← relatório final gerado
```

--- -->

## Arquivos para apresentação

| Arquivo | O que é |
|---|---|
| [Enunciado (PDF)](TechChallenge/POSTECH%20-%20%5BDTAT%5D%20-%20Tech%20Challenge%20-%20Fase%201.pdf) | Descrição oficial do Tech Challenge |
| [Notebook.ipynb](TechChallenge/Notebook.ipynb) | Análise exploratória — limpeza, visualizações e insights |
| [relatorio_executivo.pdf](TechChallenge/relatorios/relatorio_executivo.pdf) | Relatório executivo final pronto para entrega |
| [Apresentação com Slides](TechChallenge/relatorios/ATUALIZAdoImpacto%20da%20Eficiência%20Logística%20no%20E-Commerce.pptx) | Apresentação com Slides |
| [video youtube](https://www.youtube.com/watch?v=qCliC9FgAdg&feature=youtu.be) | Video para apresentação |


<!-- ---

## Como reproduzir

### 1. Instalar dependências

```bash
pip install -r requirements-dev.txt
```

### 2. Executar o notebook

Abra [`Notebook.ipynb`](TechChallenge/Notebook.ipynb) no Jupyter e execute todas as células.

### 3. Gerar o relatório executivo

```bash
cd "Fase 1/TechChallenge"
python relatorio_executivo.py
```

O PDF será salvo em `TechChallenge/relatorios/relatorio_executivo.pdf`.

> **Pré-requisito:** os CSVs do dataset Olist devem estar na pasta `TechChallenge/database/`.  
> Download: [Brazilian E-Commerce Public Dataset by Olist — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## Principais resultados

| Indicador | Valor |
|---|---|
| Pedidos entregues analisados | ~96 mil |
| Taxa de atraso | ~8% |
| Diferença de nota (no prazo vs. atrasado) | ~1,4 ponto |
| Mediana do atraso | ~3 dias |

> Os valores exatos são calculados dinamicamente ao executar o script.

---

## Limitações conhecidas

- A base cobre um período histórico específico e pode não refletir o cenário atual.
- Pedidos sem data de entrega foram excluídos da análise de atraso.
- A recompra não foi analisada por coorte ou janela temporal fixa.
- Não foram calculados ROI nem custo de intervenção. -->
