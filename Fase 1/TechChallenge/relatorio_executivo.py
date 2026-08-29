# %% [markdown]
# # RELATÓRIO EXECUTIVO
# ## Impacto da eficiência logística na satisfação e no faturamento
#
# Dataset: Brazilian E-Commerce Public Dataset by Olist
#
# Pergunta norteadora:
# Como a eficiência logística impacta o faturamento dos e-commerces brasileiros?
#
# Este relatório foi estruturado a partir do notebook Ps_Tech2.ipynb.
# Foram mantidos os temas e análises originais, mas foram corrigidos:
#
# - duplicidade causada por junções entre tabelas de diferentes granularidades;
# - soma duplicada de payment_value;
# - uso de linguagem causal sem evidência experimental;
# - ausência de metodologia formal;
# - ausência de limitações estatísticas;
# - ausência de critérios explícitos para receita em risco;
# - falta de consolidação em formato executivo.
#
# O relatório distingue:
#
# - base de pedidos: uma linha por pedido;
# - base de itens: uma linha por item;
# - análise associativa: identifica relações, mas não prova causalidade.

# %%
import base64
import html
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from weasyprint import HTML

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------
# Configurações de diretórios
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "database"
REPORT_DIR = BASE_DIR / "relatorios"

REPORT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["font.family"] = "DejaVu Sans"


# ---------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------


def carregar_csv(nome_arquivo):
    """Carrega um CSV da pasta database."""
    caminho = DATA_DIR / nome_arquivo

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}\n"
            "Verifique se os CSVs estão na pasta database."
        )

    return pd.read_csv(caminho)


def formatar_brl(valor):
    """Formata valores em reais no padrão brasileiro."""
    if pd.isna(valor):
        return "R$ 0,00"

    valor = float(valor)
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(valor, casas=1):
    """Formata uma proporção ou percentual."""
    if pd.isna(valor):
        return "0,0%"

    return f"{float(valor):.{casas}f}%".replace(".", ",")


def salvar_grafico(nome):
    """Salva o gráfico atual na pasta relatorios."""
    caminho = REPORT_DIR / nome
    plt.tight_layout()
    plt.savefig(caminho, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close()
    return caminho


def imagem_base64(caminho):
    """
    Converte uma imagem para base64.
    Isso permite incorporar os gráficos diretamente no HTML final.
    """
    with open(caminho, "rb") as arquivo:
        conteudo = base64.b64encode(arquivo.read()).decode("utf-8")

    return f"data:image/png;base64,{conteudo}"


def anotar_barras(ax, formato="{:.2f}"):
    """Adiciona rótulos às barras de um gráfico."""
    for barra in ax.patches:
        altura = barra.get_height()

        if pd.notna(altura):
            ax.annotate(
                formato.format(altura),
                (barra.get_x() + barra.get_width() / 2, altura),
                ha="center",
                va="bottom",
                xytext=(0, 5),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
            )


def verificar_unicidade(df, coluna, nome_tabela):
    """Valida se uma tabela possui uma linha por chave."""
    duplicados = df[coluna].duplicated().sum()

    if duplicados > 0:
        print(
            f"Atenção: {nome_tabela} possui {duplicados} registros "
            f"duplicados para a chave {coluna}."
        )
    else:
        print(f"{nome_tabela}: chave {coluna} sem duplicidades.")


# %% [markdown]
# ---
# ## 1. Carregamento dos dados

# %%
orders = carregar_csv("olist_orders_dataset.csv")
payments = carregar_csv("olist_order_payments_dataset.csv")
reviews = carregar_csv("olist_order_reviews_dataset.csv")
customers = carregar_csv("olist_customers_dataset.csv")
items = carregar_csv("olist_order_items_dataset.csv")
products = carregar_csv("olist_products_dataset.csv")
sellers = carregar_csv("olist_sellers_dataset.csv")

print("Arquivos carregados com sucesso.")
print(f"Pedidos: {orders.shape}")
print(f"Pagamentos: {payments.shape}")
print(f"Avaliações: {reviews.shape}")
print(f"Clientes: {customers.shape}")
print(f"Itens: {items.shape}")


# %% [markdown]
# ---
# ## 2. Preparação e controle de granularidade
#
# A tabela principal da análise financeira será construída no nível do pedido.
# Portanto, haverá apenas uma linha por `order_id`.
#
# Essa decisão evita que:
#
# - pedidos com vários pagamentos sejam repetidos;
# - pedidos com vários itens sejam repetidos;
# - uma mesma receita seja somada várias vezes.
#
# A análise de produtos, categorias e vendedores deve utilizar a tabela de
# itens separadamente.

# %%
# Conversão das datas da tabela de pedidos
colunas_data_orders = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for coluna in colunas_data_orders:
    if coluna in orders.columns:
        orders[coluna] = pd.to_datetime(orders[coluna], errors="coerce")

# Verificações iniciais
verificar_unicidade(orders, "order_id", "orders")
verificar_unicidade(customers, "customer_id", "customers")
verificar_unicidade(sellers, "seller_id", "sellers")


# %% [markdown]
# ---
# ## 3. Agregação de pagamentos por pedido
#
# A tabela de pagamentos pode conter mais de uma linha para o mesmo pedido,
# principalmente devido a diferentes formas de pagamento ou parcelas.
#
# O valor financeiro do pedido será calculado pela soma de `payment_value`
# agrupada por `order_id`.

# %%
pagamentos_pedido = payments.groupby("order_id", as_index=False).agg(
    payment_value=("payment_value", "sum"),
    payment_installments=("payment_installments", "max"),
    payment_types=(
        "payment_type",
        lambda valores: ", ".join(sorted(valores.dropna().astype(str).unique())),
    ),
)

verificar_unicidade(pagamentos_pedido, "order_id", "pagamentos_pedido")


# %% [markdown]
# ---
# ## 4. Consolidação das avaliações por pedido
#
# Algumas avaliações podem apresentar mais de um registro para o mesmo pedido.
# Para preservar uma observação por pedido, será mantida a avaliação mais
# recente disponível.
#
# Essa regra é uma decisão metodológica e deve ser informada no relatório.

# %%
if "review_answer_timestamp" in reviews.columns:
    reviews["review_answer_timestamp"] = pd.to_datetime(
        reviews["review_answer_timestamp"], errors="coerce"
    )

if "review_creation_date" in reviews.columns:
    reviews["review_creation_date"] = pd.to_datetime(
        reviews["review_creation_date"], errors="coerce"
    )

coluna_data_review = (
    "review_answer_timestamp"
    if "review_answer_timestamp" in reviews.columns
    else "review_creation_date"
)

reviews_ordenadas = reviews.sort_values(
    by=["order_id", coluna_data_review], na_position="first"
)

reviews_pedido = reviews_ordenadas.drop_duplicates(subset="order_id", keep="last")[
    ["order_id", "review_score"]
]

verificar_unicidade(reviews_pedido, "order_id", "reviews_pedido")


# %% [markdown]
# ---
# ## 5. Construção da base principal: `df_pedidos`
#
# A base principal terá uma linha por pedido.
#
# Ela será utilizada para:
#
# - atraso;
# - satisfação;
# - receita;
# - estado do cliente;
# - perfil de cliente;
# - evolução temporal;
# - retenção exploratória.

# %%
df_pedidos = (
    orders.merge(pagamentos_pedido, on="order_id", how="left", validate="one_to_one")
    .merge(reviews_pedido, on="order_id", how="left", validate="one_to_one")
    .merge(
        customers[
            [
                "customer_id",
                "customer_unique_id",
                "customer_zip_code_prefix",
                "customer_state",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
)

# Verificação obrigatória da granularidade
if df_pedidos["order_id"].duplicated().any():
    raise ValueError(
        "A base df_pedidos possui order_id duplicado. "
        "A análise financeira não pode continuar."
    )

print(f"Linhas na base de pedidos: {len(df_pedidos):,}")
print(f"Pedidos únicos: {df_pedidos['order_id'].nunique():,}")


# %% [markdown]
# ---
# ## 6. Definição das variáveis analíticas
#
# Pedidos sem data de entrega são excluídos das métricas de prazo porque não
# permitem calcular o atraso observado.
#
# Essa exclusão não significa que esses pedidos não sejam relevantes. Eles
# devem ser considerados em uma análise posterior de cancelamento, transporte
# ou falha de entrega.

# %%
df_pedidos["dias_atraso"] = (
    df_pedidos["order_delivered_customer_date"].dt.normalize()
    - df_pedidos["order_estimated_delivery_date"].dt.normalize()
).dt.days

df_pedidos["foi_atraso"] = df_pedidos["dias_atraso"] > 0

df_pedidos["mes_compra"] = (
    df_pedidos["order_purchase_timestamp"].dt.to_period("M").astype(str)
)

df_entregues = df_pedidos.dropna(
    subset=["order_delivered_customer_date", "dias_atraso"]
).copy()

df_entregues["status_entrega"] = np.where(
    df_entregues["foi_atraso"], "Com atraso", "No prazo"
)

# Definição operacional de receita em risco
df_entregues["receita_em_risco_flag"] = (df_entregues["foi_atraso"]) & (
    df_entregues["review_score"] <= 2
)

receita_em_risco = df_entregues.loc[
    df_entregues["receita_em_risco_flag"], "payment_value"
].sum()

total_pedidos_entregues = len(df_entregues)
pedidos_atrasados = int(df_entregues["foi_atraso"].sum())
taxa_atraso = pedidos_atrasados / total_pedidos_entregues * 100

print(f"Pedidos entregues analisados: {total_pedidos_entregues:,}")
print(f"Pedidos atrasados: {pedidos_atrasados:,}")
print(f"Taxa de atraso: {taxa_atraso:.2f}%")
print(f"Receita associada ao risco: {formatar_brl(receita_em_risco)}")


# %% [markdown]
# ---
# ## 7. Estatísticas de tendência central, dispersão e outliers
#
# De acordo com as aulas de Estatística Essencial para Analytics, a média não
# deve ser usada isoladamente quando a distribuição apresenta assimetria ou
# valores extremos.
#
# Por isso, são apresentados:
#
# - média;
# - mediana;
# - desvio-padrão;
# - primeiro e terceiro quartis;
# - IQR;
# - percentil 90;
# - limites para identificação exploratória de outliers.

# %%
dias_atraso_validos = df_entregues["dias_atraso"].dropna()

q1 = dias_atraso_validos.quantile(0.25)
q3 = dias_atraso_validos.quantile(0.75)
iqr = q3 - q1

limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr

outliers_atraso = dias_atraso_validos[
    (dias_atraso_validos < limite_inferior) | (dias_atraso_validos > limite_superior)
]

estatisticas_atraso = {
    "n": int(dias_atraso_validos.count()),
    "media": dias_atraso_validos.mean(),
    "mediana": dias_atraso_validos.median(),
    "desvio_padrao": dias_atraso_validos.std(),
    "minimo": dias_atraso_validos.min(),
    "maximo": dias_atraso_validos.max(),
    "q1": q1,
    "q3": q3,
    "iqr": iqr,
    "p90": dias_atraso_validos.quantile(0.90),
    "outliers_iqr": len(outliers_atraso),
}

print("\nEstatísticas de atraso:")
for chave, valor in estatisticas_atraso.items():
    print(f"{chave}: {valor}")


# %% [markdown]
# ---
# ## 8. Impacto associado do atraso na satisfação
#
# O resultado abaixo deve ser interpretado como associação:
#
# pedidos atrasados apresentaram determinada avaliação média, enquanto pedidos
# no prazo apresentaram outra avaliação média.
#
# O resultado não prova que o atraso seja o único causador da nota, pois outros
# fatores podem influenciar a avaliação.

# %%
satisfacao = (
    df_entregues.dropna(subset=["review_score"])
    .groupby("status_entrega")
    .agg(
        pedidos=("order_id", "nunique"),
        nota_media=("review_score", "mean"),
        nota_mediana=("review_score", "median"),
        desvio_padrao=("review_score", "std"),
        percentual_notas_baixas=("review_score", lambda x: (x <= 2).mean() * 100),
    )
    .reset_index()
)

ordem_status = ["No prazo", "Com atraso"]
satisfacao["ordem"] = satisfacao["status_entrega"].map({"No prazo": 0, "Com atraso": 1})
satisfacao = satisfacao.sort_values("ordem")

# Gráfico
plt.figure(figsize=(9, 6))
ax = sns.barplot(
    data=satisfacao,
    x="status_entrega",
    y="nota_media",
    hue="status_entrega",
    palette={"No prazo": "#2D6A4F", "Com atraso": "#D90429"},
    legend=False,
)

ax.set_title(
    "Avaliação média segundo o status da entrega", fontsize=15, fontweight="bold"
)
ax.set_xlabel("Status da entrega")
ax.set_ylabel("Nota média")
ax.set_ylim(0, 5)

anotar_barras(ax, "{:.2f}")
grafico_satisfacao = salvar_grafico("satisfacao_por_status.png")


# %% [markdown]
# ---
# ## 9. Receita associada ao risco por estado
#
# A receita em risco é definida neste relatório como o valor pago em pedidos
# atrasados que receberam nota igual ou inferior a 2.
#
# O indicador representa exposição financeira associada a uma experiência
# negativa. Ele não representa perda efetiva nem previsão de perda futura.

# %%
risco_estado = (
    df_entregues[df_entregues["receita_em_risco_flag"]]
    .groupby("customer_state", as_index=False)
    .agg(
        receita_em_risco=("payment_value", "sum"),
        pedidos_em_risco=("order_id", "nunique"),
    )
    .sort_values("receita_em_risco", ascending=False)
)

plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=risco_estado.head(10),
    x="receita_em_risco",
    y="customer_state",
    hue="customer_state",
    palette="Reds_r",
    legend=False,
)

ax.set_title(
    "Estados com maior receita associada ao risco", fontsize=15, fontweight="bold"
)
ax.set_xlabel("Receita associada ao risco")
ax.set_ylabel("Estado")

for barra in ax.patches:
    valor = barra.get_width()

    ax.annotate(
        formatar_brl(valor),
        (valor, barra.get_y() + barra.get_height() / 2),
        ha="left",
        va="center",
        xytext=(5, 0),
        textcoords="offset points",
        fontsize=8,
    )

grafico_estado = salvar_grafico("risco_por_estado.png")


# %% [markdown]
# ---
# ## 10. Perfil do cliente e receita associada ao risco
#
# O perfil é definido no nível do cliente único:
#
# - novo cliente: apenas um pedido na base;
# - recorrente: mais de um pedido na base.
#
# Essa classificação é descritiva e não equivale a uma análise completa de
# Lifetime Value, pois a base possui período histórico limitado.

# %%
frequencia_cliente = df_pedidos.groupby("customer_unique_id", as_index=False).agg(
    total_pedidos=("order_id", "nunique")
)

df_entregues = df_entregues.merge(
    frequencia_cliente, on="customer_unique_id", how="left", validate="many_to_one"
)

df_entregues["perfil_cliente"] = np.where(
    df_entregues["total_pedidos"] > 1, "Cliente recorrente", "Novo cliente"
)

risco_perfil = (
    df_entregues[df_entregues["receita_em_risco_flag"]]
    .groupby("perfil_cliente", as_index=False)
    .agg(
        receita_em_risco=("payment_value", "sum"),
        pedidos_em_risco=("order_id", "nunique"),
    )
)

plt.figure(figsize=(9, 6))
ax = sns.barplot(
    data=risco_perfil,
    x="perfil_cliente",
    y="receita_em_risco",
    hue="perfil_cliente",
    palette={
        "Novo cliente": "#D90429",
        "Cliente recorrente": "#F48C06",
    },
    legend=False,
)

ax.set_title(
    "Receita associada ao risco por perfil de cliente", fontsize=15, fontweight="bold"
)
ax.set_xlabel("Perfil do cliente")
ax.set_ylabel("Receita associada ao risco")

for barra in ax.patches:
    valor = barra.get_height()

    ax.annotate(
        formatar_brl(valor),
        (barra.get_x() + barra.get_width() / 2, valor),
        ha="center",
        va="bottom",
        xytext=(0, 5),
        textcoords="offset points",
        fontsize=9,
    )

grafico_perfil = salvar_grafico("risco_por_perfil.png")


# %% [markdown]
# ---
# ## 11. Evolução mensal do risco
#
# O gráfico apresenta a evolução mensal da receita associada a pedidos
# atrasados com avaliação baixa.
#
# A existência de um pico mensal não prova, isoladamente, que ele seja causado
# pela Black Friday ou pelo Natal. Essa interpretação exige comparação com
# volume de pedidos, taxa de atraso e sazonalidade de anos diferentes.

# %%
risco_mensal = (
    df_entregues[df_entregues["receita_em_risco_flag"]]
    .groupby("mes_compra", as_index=False)
    .agg(
        receita_em_risco=("payment_value", "sum"),
        pedidos_em_risco=("order_id", "nunique"),
    )
    .sort_values("mes_compra")
)

plt.figure(figsize=(14, 6))
ax = sns.lineplot(
    data=risco_mensal,
    x="mes_compra",
    y="receita_em_risco",
    marker="o",
    color="#D90429",
    linewidth=2.5,
)

ax.set_title(
    "Evolução mensal da receita associada ao risco", fontsize=15, fontweight="bold"
)
ax.set_xlabel("Mês da compra")
ax.set_ylabel("Receita associada ao risco")
plt.xticks(rotation=45)

grafico_mensal = salvar_grafico("risco_mensal.png")


# %% [markdown]
# ---
# ## 12. Retenção exploratória após a primeira experiência
#
# A análise identifica se o cliente realizou mais de um pedido na base.
#
# Essa métrica não prova que a nota causou ou impediu a recompra, porque:
#
# - não há controle experimental;
# - não foi aplicada uma janela fixa após a primeira compra;
# - clientes que compraram no final do período tiveram menos tempo para retornar;
# - outros fatores podem explicar a recompra.

# %%
df_cliente_ordem = df_pedidos.sort_values(
    ["customer_unique_id", "order_purchase_timestamp"]
).copy()

primeiro_pedido = df_cliente_ordem.drop_duplicates("customer_unique_id", keep="first")[
    ["customer_unique_id", "review_score"]
]

contagem_pedidos = df_pedidos.groupby("customer_unique_id", as_index=False).agg(
    total_pedidos=("order_id", "nunique")
)

retencao = primeiro_pedido.merge(
    contagem_pedidos, on="customer_unique_id", how="left", validate="one_to_one"
)

retencao["voltou_a_comprar"] = retencao["total_pedidos"] > 1

retencao["satisfacao_inicial"] = np.select(
    [
        retencao["review_score"] <= 3,
        retencao["review_score"] == 4,
        retencao["review_score"] == 5,
    ],
    [
        "Notas 1 a 3",
        "Nota 4",
        "Nota 5",
    ],
    default="Sem avaliação",
)

taxa_retorno = (
    retencao[retencao["satisfacao_inicial"] != "Sem avaliação"]
    .groupby("satisfacao_inicial", as_index=False)
    .agg(
        clientes=("customer_unique_id", "nunique"),
        taxa_retorno=("voltou_a_comprar", "mean"),
    )
)

taxa_retorno["taxa_retorno_percentual"] = taxa_retorno["taxa_retorno"] * 100

ordem_retorno = {
    "Notas 1 a 3": 0,
    "Nota 4": 1,
    "Nota 5": 2,
}

taxa_retorno["ordem"] = taxa_retorno["satisfacao_inicial"].map(ordem_retorno)
taxa_retorno = taxa_retorno.sort_values("ordem")

plt.figure(figsize=(9, 6))
ax = sns.barplot(
    data=taxa_retorno,
    x="satisfacao_inicial",
    y="taxa_retorno_percentual",
    hue="satisfacao_inicial",
    palette=["#D90429", "#F48C06", "#2D6A4F"],
    legend=False,
)

ax.set_title(
    "Retorno observado segundo a avaliação da primeira experiência",
    fontsize=15,
    fontweight="bold",
)
ax.set_xlabel("Avaliação da primeira experiência")
ax.set_ylabel("Clientes com mais de um pedido (%)")

for barra in ax.patches:
    valor = barra.get_height()

    ax.annotate(
        formatar_percentual(valor, 2),
        (barra.get_x() + barra.get_width() / 2, valor),
        ha="center",
        va="bottom",
        xytext=(0, 5),
        textcoords="offset points",
        fontsize=9,
    )

grafico_retorno = salvar_grafico("retorno_por_satisfacao.png")


# %% [markdown]
# ---
# ## 13. Gargalo logístico: vendedor vs. transportadora
#
# Compara o tempo médio de cada etapa da cadeia logística em pedidos atrasados.
# Etapa 1: da compra até a postagem na transportadora (responsabilidade do vendedor).
# Etapa 2: da postagem até a entrega ao cliente (responsabilidade da transportadora).

# %%
df_entregues["tempo_postagem"] = (
    df_entregues["order_delivered_carrier_date"]
    - df_entregues["order_purchase_timestamp"]
).dt.days

df_entregues["tempo_transporte_etapa"] = (
    df_entregues["order_delivered_customer_date"]
    - df_entregues["order_delivered_carrier_date"]
).dt.days

df_gargalo = df_entregues[df_entregues["foi_atraso"]].dropna(
    subset=["tempo_postagem", "tempo_transporte_etapa"]
)

tempo_medio_postagem = df_gargalo["tempo_postagem"].mean()
tempo_medio_transporte = df_gargalo["tempo_transporte_etapa"].mean()

dados_gargalo = pd.DataFrame(
    {
        "Etapa": [
            "Vendedor\n(da compra à postagem)",
            "Transportadora\n(da postagem à entrega)",
        ],
        "Média de dias": [tempo_medio_postagem, tempo_medio_transporte],
    }
)

plt.figure(figsize=(9, 6))
ax = sns.barplot(
    data=dados_gargalo,
    x="Etapa",
    y="Média de dias",
    hue="Etapa",
    palette=["#FFD700", "#D90429"],
    legend=False,
)

ax.set_title(
    "Gargalo logístico: onde o tempo é maior?\n(apenas pedidos atrasados)",
    fontsize=15,
    fontweight="bold",
)
ax.set_ylabel("Média de dias (pedidos atrasados)")
ax.set_xlabel("")

anotar_barras(ax, "{:.1f}")
grafico_gargalo = salvar_grafico("gargalo_logistico.png")


# %% [markdown]
# ---
# ## 14. Sazonalidade da receita em risco com destaque para Black Friday
#
# A mesma série mensal calculada na seção 11, agora com destaque visual
# para o período de pico sazonal (nov/2017 a fev/2018).
# O pico não pode ser atribuído diretamente a esses eventos sem comparação
# com volumes equivalentes em anos anteriores e controle da taxa de atraso.

# %%
plt.figure(figsize=(14, 6))
ax = sns.lineplot(
    data=risco_mensal,
    x="mes_compra",
    y="receita_em_risco",
    marker="o",
    color="#D90429",
    linewidth=2.5,
)

ax.set_title(
    "Evolução Mensal da Receita em Risco (Atrasos Críticos)",
    fontsize=15,
    fontweight="bold",
)
ax.set_xlabel("Mês da Compra")
ax.set_ylabel("Volume Financeiro em Risco (R$)")
plt.xticks(rotation=45)

meses_risco = risco_mensal["mes_compra"].tolist()
if "2017-11" in meses_risco and "2018-02" in meses_risco:
    x_ini = meses_risco.index("2017-11") - 0.5
    x_fim = meses_risco.index("2018-02") + 0.5
    ax.axvspan(
        x_ini,
        x_fim,
        color="red",
        alpha=0.10,
        label="Pico Sazonal (Black Friday/Natal)",
    )
    ax.legend()

grafico_sazonalidade = salvar_grafico("sazonalidade_risco.png")


# %% [markdown]
# ---
# ## 15. Impacto da distância no desempenho logístico
#
# Calcula a distância entre o CEP do vendedor e o CEP do cliente usando a
# fórmula de Haversine, com coordenadas médias por prefixo de CEP.
# A análise preserva granularidade de um pedido por linha (order_id único),
# selecionando o primeiro seller_id registrado nos itens de cada pedido.
# Os pedidos são agrupados em faixas de distância para avaliar se a
# quilometragem explica a taxa de atraso e o tempo de transporte.

# %%
geo = carregar_csv("olist_geolocation_dataset.csv")
geo_reduzido = (
    geo.groupby("geolocation_zip_code_prefix")[["geolocation_lat", "geolocation_lng"]]
    .mean()
    .reset_index()
)

# Um vendedor por pedido: primeiro seller_id listado nos itens do pedido
seller_por_pedido = items.groupby("order_id")["seller_id"].first().reset_index()

df_distancia = (
    df_entregues[
        [
            "order_id",
            "customer_zip_code_prefix",
            "foi_atraso",
            "dias_atraso",
            "tempo_transporte_etapa",
        ]
    ]
    .merge(seller_por_pedido, on="order_id", how="left")
    .merge(
        sellers[["seller_id", "seller_zip_code_prefix"]],
        on="seller_id",
        how="left",
    )
    .merge(
        geo_reduzido.rename(
            columns={
                "geolocation_zip_code_prefix": "customer_zip_code_prefix",
                "geolocation_lat": "lat_cust",
                "geolocation_lng": "lng_cust",
            }
        ),
        on="customer_zip_code_prefix",
        how="left",
    )
    .merge(
        geo_reduzido.rename(
            columns={
                "geolocation_zip_code_prefix": "seller_zip_code_prefix",
                "geolocation_lat": "lat_seller",
                "geolocation_lng": "lng_seller",
            }
        ),
        on="seller_zip_code_prefix",
        how="left",
    )
    .dropna(subset=["lat_cust", "lng_cust", "lat_seller", "lng_seller"])
)

pedidos_excluidos_distancia = len(df_entregues) - len(df_distancia)
print(
    "Pedidos excluídos da análise de distância "
    f"(sem correspondência na geolocalização): {pedidos_excluidos_distancia:,}"
)


def haversine(lat1, lon1, lat2, lon2):
    """Distância em km entre dois pontos geográficos (fórmula de Haversine)."""
    r = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = (
        np.sin(delta_phi / 2) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    )
    return r * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


df_distancia["distancia_km"] = haversine(
    df_distancia["lat_cust"],
    df_distancia["lng_cust"],
    df_distancia["lat_seller"],
    df_distancia["lng_seller"],
)

correlacao_distancia = df_distancia["distancia_km"].corr(df_distancia["dias_atraso"])

max_dist = df_distancia["distancia_km"].max()
bins_dist = [0, 250, 500, 1000, 2000, max(max_dist + 1, 2001)]
labels_dist = [
    "Até 250km",
    "250–500km",
    "500–1000km",
    "1000–2000km",
    "Acima 2000km",
]

df_distancia["faixa_distancia"] = pd.cut(
    df_distancia["distancia_km"],
    bins=bins_dist,
    labels=labels_dist,
    right=True,
    include_lowest=True,
)

analise_distancia = (
    df_distancia.groupby("faixa_distancia", observed=False)
    .agg(
        taxa_atraso=("foi_atraso", "mean"),
        tempo_transporte_medio=("tempo_transporte_etapa", "mean"),
        pedidos=("order_id", "nunique"),
    )
    .reset_index()
)
analise_distancia["taxa_atraso_pct"] = analise_distancia["taxa_atraso"] * 100

fig_dist, ax1_dist = plt.subplots(figsize=(14, 7))

barras_dist = sns.barplot(
    data=analise_distancia,
    x="faixa_distancia",
    y="tempo_transporte_medio",
    ax=ax1_dist,
    hue="faixa_distancia",
    palette="Blues_d",
    alpha=0.8,
    legend=False,
)
ax1_dist.set_ylabel(
    "Tempo médio de transporte (dias)",
    fontsize=11,
    fontweight="bold",
    color="navy",
)
ax1_dist.set_xlabel("Faixa de distância entre vendedor e comprador", fontsize=11)

ax2_dist = ax1_dist.twinx()
sns.lineplot(
    data=analise_distancia,
    x="faixa_distancia",
    y="taxa_atraso_pct",
    ax=ax2_dist,
    marker="o",
    color="#D90429",
    linewidth=2.5,
    label="Taxa de atraso (%)",
)
ax2_dist.set_ylabel(
    "Taxa de atraso (%)", fontsize=11, fontweight="bold", color="#D90429"
)
ax2_dist.grid(False)
ax2_dist.legend(loc="upper left")

for p in barras_dist.patches:
    h = p.get_height()
    if pd.notna(h) and h > 0:
        ax1_dist.annotate(
            f"{h:.1f} d",
            (p.get_x() + p.get_width() / 2, h),
            ha="center",
            va="bottom",
            xytext=(0, 5),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
        )

ax1_dist.set_title(
    "Distância vs. desempenho logístico: tempo de transporte e taxa de atraso",
    fontsize=14,
    fontweight="bold",
    pad=20,
)

plt.tight_layout()
grafico_distancia = salvar_grafico("distancia_desempenho.png")


# %% [markdown]
# ---
# ## 16. Peso do produto e frete vs. atraso
#
# Scatterplots com correlação calculada dinamicamente via df.corr().
# Correlação próxima de zero indica ausência de relação linear relevante
# entre as variáveis e o atraso observado.

# %%
df_itens_produto = items.merge(
    products[["product_id", "product_weight_g"]], on="product_id", how="left"
)

# Agrega por pedido: peso médio e frete total (preserva granularidade de pedido)
item_por_pedido = df_itens_produto.groupby("order_id", as_index=False).agg(
    freight_value_total=("freight_value", "sum"),
    product_weight_g_medio=("product_weight_g", "mean"),
)

df_scatter = (
    df_entregues[df_entregues["foi_atraso"]][["order_id", "dias_atraso"]]
    .merge(item_por_pedido, on="order_id", how="left")
    .dropna(subset=["product_weight_g_medio", "freight_value_total"])
)

pedidos_scatter = len(df_scatter)
corr_peso = df_scatter["product_weight_g_medio"].corr(df_scatter["dias_atraso"])
corr_frete = df_scatter["freight_value_total"].corr(df_scatter["dias_atraso"])

print(f"Pedidos com peso e frete disponíveis: {pedidos_scatter:,}")
print(f"Correlação peso médio vs. atraso: {corr_peso:.2f}")
print(f"Correlação frete total vs. atraso: {corr_frete:.2f}")

fig_scatter, (ax_peso, ax_frete) = plt.subplots(1, 2, figsize=(14, 6))

sns.scatterplot(
    data=df_scatter,
    x="product_weight_g_medio",
    y="dias_atraso",
    alpha=0.3,
    color="gray",
    ax=ax_peso,
)
ax_peso.set_title(
    f"Peso médio vs. atraso\n(Correlação: {corr_peso:.2f} — quase nula)",
    fontsize=11,
    fontweight="bold",
)
ax_peso.set_xlabel("Peso médio do produto (g)")
ax_peso.set_ylabel("Dias de atraso")

sns.scatterplot(
    data=df_scatter,
    x="freight_value_total",
    y="dias_atraso",
    alpha=0.3,
    color="gray",
    ax=ax_frete,
)
ax_frete.set_title(
    f"Frete total vs. atraso\n(Correlação: {corr_frete:.2f} — quase nula)",
    fontsize=11,
    fontweight="bold",
)
ax_frete.set_xlabel("Valor total do frete (R$)")
ax_frete.set_ylabel("Dias de atraso")

plt.suptitle(
    "Relação entre características da carga e atraso nas entregas",
    fontsize=14,
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()
grafico_peso_frete = salvar_grafico("peso_frete_atraso.png")


# %% [markdown]
# ---
# ## 17. Distribuição mensal de avaliações
#
# Gráfico de barras empilhadas com distribuição percentual de review_score
# por mês, usando pd.crosstab com normalize="index".
# Permite observar a evolução da qualidade percebida ao longo do tempo.

# %%
df_com_nota = df_pedidos.dropna(subset=["review_score", "mes_compra"])

dist_percentual = (
    pd.crosstab(
        df_com_nota["mes_compra"], df_com_nota["review_score"], normalize="index"
    )
    * 100
)

plt.figure(figsize=(18, 8))
sns.set_theme(style="white")

cores_notas = ["#D90429", "#F48C06", "#FFBA08", "#80B918", "#2D6A4F"]

dist_percentual.plot(
    kind="bar",
    stacked=True,
    color=cores_notas[: dist_percentual.shape[1]],
    ax=plt.gca(),
    width=0.85,
    alpha=0.9,
)

plt.title(
    "Distribuição mensal de avaliações (2016–2018)",
    fontsize=16,
    fontweight="bold",
    pad=20,
)
plt.xlabel("Mês da operação", fontsize=12)
plt.ylabel("Percentual das avaliações (%)", fontsize=12)
plt.legend(
    title="Review Score",
    bbox_to_anchor=(1.01, 1),
    loc="upper left",
    frameon=False,
)
plt.xticks(rotation=45, ha="right")
plt.ylim(0, 100)
sns.despine()

plt.tight_layout()
grafico_dist_mensal = salvar_grafico("distribuicao_mensal_avaliacoes.png")


# %% [markdown]
# ---
# ## 18. Relatório executivo em HTML
#
# O HTML utiliza uma estrutura visual inspirada nas recomendações de
# apresentação acadêmica:
#
# - papel A4;
# - margem superior e esquerda de 3 cm;
# - margem inferior e direita de 2 cm;
# - fonte Times New Roman;
# - corpo em tamanho 12;
# - espaçamento de 1,5;
# - texto justificado;
# - títulos numerados;
# - tabelas com identificação;
# - figuras com legenda e fonte.
#
# A ABNT não determina um modelo único de dashboard executivo. Portanto, as
# regras abaixo são uma adaptação acadêmica para o relatório analítico.

# %%
nota_no_prazo = (
    satisfacao.loc[satisfacao["status_entrega"] == "No prazo", "nota_media"].iloc[0]
    if "No prazo" in satisfacao["status_entrega"].values
    else np.nan
)

nota_atraso = (
    satisfacao.loc[satisfacao["status_entrega"] == "Com atraso", "nota_media"].iloc[0]
    if "Com atraso" in satisfacao["status_entrega"].values
    else np.nan
)

diferenca_nota = nota_no_prazo - nota_atraso

mediana_atraso = estatisticas_atraso["mediana"]
p90_atraso = estatisticas_atraso["p90"]

percentual_pedidos_sem_entrega = (
    orders["order_delivered_customer_date"].isna().mean() * 100
)

data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")

tabela_satisfacao = satisfacao[
    [
        "status_entrega",
        "pedidos",
        "nota_media",
        "nota_mediana",
        "desvio_padrao",
        "percentual_notas_baixas",
    ]
].copy()

tabela_satisfacao.columns = [
    "Status da entrega",
    "Pedidos",
    "Nota média",
    "Nota mediana",
    "Desvio-padrão",
    "Notas baixas (%)",
]

tabela_satisfacao_html = tabela_satisfacao.to_html(
    index=False,
    classes="tabela",
    float_format=lambda valor: f"{valor:.2f}".replace(".", ","),
)

tabela_estados_html = risco_estado.head(10).copy()
tabela_estados_html["receita_em_risco"] = tabela_estados_html["receita_em_risco"].map(
    formatar_brl
)

tabela_estados_html = tabela_estados_html.rename(
    columns={
        "customer_state": "Estado",
        "receita_em_risco": "Receita associada ao risco",
        "pedidos_em_risco": "Pedidos em risco",
    }
)[
    [
        "Estado",
        "Receita associada ao risco",
        "Pedidos em risco",
    ]
].to_html(
    index=False, classes="tabela"
)


def figura_html(caminho, numero, titulo):
    imagem = imagem_base64(caminho)

    return f"""
    <figure>
        <img src="{imagem}" alt="{html.escape(titulo)}">
        <figcaption>
            Figura {numero} — {html.escape(titulo)}.
            Fonte: elaboração própria com base nos dados da Olist.
        </figcaption>
    </figure>
    """


sumario_html = """
<section class="sumario">
<h2>Sumário</h2>
<ol>
<li><a href="#resumo-executivo">Resumo executivo</a></li>
<li><a href="#objetivos">Objetivos</a>
    <ol>
    <li><a href="#objetivo-geral">Objetivo geral</a></li>
    <li><a href="#objetivos-especificos">Objetivos específicos</a></li>
    </ol>
</li>
<li><a href="#metodologia">Metodologia</a>
    <ol>
    <li><a href="#unidade-analise">Unidade de análise</a></li>
    <li><a href="#definicao-atraso">Definição de atraso</a></li>
    <li><a href="#definicao-receita-risco">Definição de receita associada ao risco</a></li>
    <li><a href="#tratamento-estatistico">Tratamento estatístico</a></li>
    </ol>
</li>
<li><a href="#resultados">Resultados</a>
    <ol>
    <li><a href="#desempenho-entrega-satisfacao">Desempenho da entrega e satisfação</a></li>
    <li><a href="#estatisticas-atraso">Estatísticas de atraso, dispersão e outliers</a></li>
    <li><a href="#exposicao-estado">Exposição financeira por estado</a></li>
    <li><a href="#gargalo-logistico">Gargalo logístico: vendedor versus transportadora</a></li>
    <li><a href="#sazonalidade-risco">Sazonalidade da receita em risco</a></li>
    <li><a href="#peso-frete-atraso">Relação entre peso do produto, frete e atraso</a></li>
    <li><a href="#distancia-desempenho">Impacto da distância no desempenho logístico</a></li>
    <li><a href="#distribuicao-avaliacoes">Distribuição mensal de avaliações</a></li>
    <li><a href="#perfil-cliente">Perfil do cliente observado</a></li>
    <li><a href="#retencao-exploratoria">Retenção exploratória após a primeira experiência</a></li>
    </ol>
</li>
<li><a href="#recomendacoes">Recomendações executivas</a></li>
<li><a href="#limitacoes">Limitações</a></li>
<li><a href="#conclusao">Conclusão</a></li>
<li><a href="#referencias">Referências</a></li>
</ol>
</section>
"""


html_relatorio = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">

<title>
Relatório Executivo — Eficiência Logística e Faturamento
</title>

<style>

@page {{
    size: A4;
    margin: 3cm 2cm 2cm 3cm;
}}

body {{
    font-family: "Times New Roman", Times, serif;
    font-size: 12pt;
    line-height: 1.5;
    text-align: justify;
    color: #222;
    background: white;
}}

h1, h2, h3 {{
    font-family: "Times New Roman", Times, serif;
    text-align: left;
}}

h1 {{
    text-align: center;
    font-size: 18pt;
    margin-top: 80px;
    margin-bottom: 40px;
}}

h2 {{
    font-size: 14pt;
    margin-top: 28px;
    margin-bottom: 12px;
}}

h3 {{
    font-size: 12pt;
    margin-top: 20px;
}}

.capa {{
    text-align: center;
    page-break-after: always;
}}

.capa p {{
    text-align: center;
}}

.sumario {{
    page-break-after: always;
    margin: 20px 0 30px 0;
}}

.sumario ol {{
    margin-top: 8px;
}}

.sumario a {{
    text-decoration: none;
    color: #222;
}}

.resumo-executivo {{
    border: 1px solid #999;
    padding: 15px;
    margin: 18px 0;
}}

.kpi {{
    border: 1px solid #bbb;
    padding: 10px;
    margin: 8px 0;
    background-color: #f7f7f7;
}}

.kpi strong {{
    font-size: 14pt;
}}

.tabela {{
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0 5px 0;
    font-size: 10pt;
}}

.tabela th,
.tabela td {{
    border: 1px solid #777;
    padding: 6px;
}}

.tabela th {{
    background-color: #eaeaea;
    text-align: center;
}}

.tabela td {{
    text-align: left;
}}

figure {{
    text-align: center;
    margin: 22px 0;
    page-break-inside: avoid;
}}

figure img {{
    max-width: 100%;
    height: auto;
}}

figcaption {{
    font-size: 10pt;
    text-align: center;
    margin-top: 5px;
}}

.nota-metodologica {{
    background-color: #f5f5f5;
    border-left: 4px solid #555;
    padding: 12px;
    margin: 15px 0;
}}

ul {{
    margin-top: 5px;
}}

.referencia {{
    text-align: left;
    margin-left: 0;
    text-indent: -1.25cm;
    padding-left: 1.25cm;
    margin-bottom: 8px;
}}

.page-break {{
    page-break-before: always;
}}

</style>
</head>

<body>

<section class="capa">
    <p><strong>RELATÓRIO EXECUTIVO</strong></p>
    <p>DATA ANALYTICS</p>

    <h1>
        Impacto da eficiência logística na satisfação e no faturamento
    </h1>

    <p>
        Análise exploratória do Brazilian E-Commerce Public Dataset by Olist
    </p>

    <br><br><br>

    <p>Julia Ayumi Suzuki</p>
    <p>Pâmela Cristina da Silva</p>
    <p>Larissa Nicoli Rodrigues</p>
    <p>Matheus Silva de Jesus</p>
    <p>Paulo Jean Alves da Silva</p>
    <p>São Paulo</p>
    <p>{datetime.now().year}</p>
</section>

{sumario_html}

<h2 id="resumo-executivo">Resumo executivo</h2>

<div class="resumo-executivo">
<p>
Este relatório analisa a associação entre desempenho logístico, satisfação do
cliente e exposição financeira no comércio eletrônico brasileiro. A unidade
principal de análise foi o pedido, garantindo que o valor pago não fosse
contabilizado repetidamente em razão da existência de múltiplos pagamentos,
avaliações ou itens.
</p>

<p>
A receita associada ao risco foi definida como o valor pago em pedidos entregues
com atraso e avaliados com nota igual ou inferior a 2. Essa definição representa
uma exposição financeira associada a uma experiência negativa, mas não equivale
a uma perda efetiva nem permite estimar, isoladamente, o faturamento futuro.
</p>

<p>
Os resultados devem ser interpretados como evidências descritivas e associativas.
Eles apoiam a priorização de investigações logísticas, mas não comprovam que o
atraso seja o único responsável pela insatisfação ou pela ausência de recompra.
</p>
</div>

<div class="kpi">
<strong>{total_pedidos_entregues:,}</strong><br>
pedidos entregues considerados na análise.
</div>

<div class="kpi">
<strong>{formatar_percentual(taxa_atraso)}</strong><br>
taxa de pedidos atrasados.
</div>

<div class="kpi">
<strong>{formatar_brl(receita_em_risco)}</strong><br>
receita associada ao risco operacional.
</div>

<h2 id="objetivos">1 Objetivos</h2>

<h3 id="objetivo-geral">1.1 Objetivo geral</h3>

<p>
Analisar como o desempenho logístico está associado à satisfação dos clientes e
à exposição financeira da operação de comércio eletrônico.
</p>

<h3 id="objetivos-especificos">1.2 Objetivos específicos</h3>

<ul>
<li>Comparar a satisfação de pedidos entregues no prazo e com atraso;</li>
<li>estimar a receita associada a pedidos atrasados com avaliações baixas;</li>
<li>identificar estados com maior concentração de exposição financeira;</li>
<li>examinar a distribuição dos atrasos e seus valores extremos;</li>
<li>analisar diferenças descritivas entre clientes novos e recorrentes;</li>
<li>avaliar, de forma exploratória, a relação entre primeira avaliação e retorno.</li>
</ul>

<h2 id="metodologia">2 Metodologia</h2>

<p>
A análise foi desenvolvida com Python, utilizando as bibliotecas Pandas,
NumPy, Matplotlib e Seaborn. Foram utilizadas as tabelas de pedidos,
pagamentos, avaliações, clientes, itens, produtos e vendedores do conjunto de
dados público da Olist.
</p>

<h3 id="unidade-analise">2.1 Unidade de análise</h3>

<p>
A análise financeira e de satisfação foi realizada no nível do pedido, com uma
linha por <code>order_id</code>. Pagamentos foram agregados por pedido e as
avaliações foram consolidadas, mantendo-se o registro mais recente disponível.
</p>

<p>
A análise de produtos, categorias e vendedores deve ser realizada no nível dos
itens. Essas duas granularidades não devem ser misturadas quando houver soma de
valores financeiros do pedido.
</p>

<h3 id="definicao-atraso">2.2 Definição de atraso</h3>

<p>
Um pedido foi classificado como atrasado quando a data efetiva de entrega ao
cliente foi posterior à data estimada de entrega:
<strong>dias de atraso > 0</strong>.
</p>

<h3 id="definicao-receita-risco">2.3 Definição de receita associada ao risco</h3>

<p>
Foi considerado associado ao risco o valor pago em pedidos que atenderam
simultaneamente às condições de atraso e avaliação igual ou inferior a 2.
</p>

<div class="nota-metodologica">
<strong>Nota metodológica:</strong>
essa métrica não representa perda financeira comprovada, churn, LTV ou ROI.
Ela representa uma medida descritiva de exposição financeira associada a uma
experiência operacional negativa.
</div>

<h3 id="tratamento-estatistico">2.4 Tratamento estatístico</h3>

<p>
Foram utilizadas média, mediana, desvio-padrão, quartis, intervalo
interquartílico e percentil 90. A mediana e os percentis foram incluídos porque
tempos de entrega podem apresentar assimetria e valores extremos.
</p>

<h2 id="resultados">3 Resultados</h2>

<h3 id="desempenho-entrega-satisfacao">3.1 Desempenho da entrega e satisfação</h3>

<p>
A avaliação média dos pedidos entregues no prazo foi de
<strong>{nota_no_prazo:.2f}</strong>, enquanto a avaliação média dos pedidos
atrasados foi de <strong>{nota_atraso:.2f}</strong>.
</p>

<p>
A diferença descritiva entre os grupos foi de
<strong>{diferenca_nota:.2f} ponto(s)</strong>. Esse resultado indica uma
associação entre atraso e menor avaliação média na base analisada. Entretanto,
não permite afirmar que o atraso seja a única causa da avaliação, pois fatores
como produto, preço, frete, atendimento e expectativa do cliente também podem
influenciar a nota.
</p>

{figura_html(grafico_satisfacao, 1, "Avaliação média segundo o status da entrega")}

<h3 id="estatisticas-atraso">3.2 Estatísticas de atraso, dispersão e outliers</h3>

<p>
O atraso apresentou mediana de
<strong>{mediana_atraso:.1f} dia(s)</strong> e percentil 90 de
<strong>{p90_atraso:.1f} dia(s)</strong>. O percentil 90 indica o valor abaixo
do qual se encontram aproximadamente 90% das observações válidas de prazo.
</p>

<p>
Foram identificadas, pelo critério exploratório do IQR,
<strong>{estatisticas_atraso["outliers_iqr"]:,}</strong> observações
potencialmente extremas. Esses registros não foram removidos automaticamente,
porque um outlier pode representar erro, evento excepcional ou ocorrência real
de interesse operacional.
</p>

<h3 id="exposicao-estado">3.3 Exposição financeira por estado</h3>

<p>
Os estados com maior valor absoluto de receita associada ao risco estão
apresentados abaixo. A concentração em determinado estado pode refletir tanto
maior risco relativo quanto maior volume de pedidos. Por isso, a decisão
gerencial deve considerar também taxas proporcionais, e não apenas valores
absolutos.
</p>

{figura_html(grafico_estado, 2, "Estados com maior receita associada ao risco")}

{tabela_estados_html}

<p>
Tabela 1 — Estados com maior receita associada ao risco.
Fonte: elaboração própria com base nos dados da Olist.
</p>

<h3 id="gargalo-logistico">3.4 Gargalo logístico: vendedor versus transportadora</h3>

<p>
A cadeia logística foi dividida em duas etapas: o intervalo entre a data da
compra e a postagem na transportadora (etapa do vendedor) e o intervalo entre
a postagem e a entrega ao cliente (etapa da transportadora). A análise
considerou apenas pedidos com atraso.
</p>

<p>
O tempo médio na etapa do vendedor foi de
<strong>{tempo_medio_postagem:.1f} dia(s)</strong>, enquanto o tempo médio
na etapa da transportadora foi de
<strong>{tempo_medio_transporte:.1f} dia(s)</strong>. Esses valores são
descritivos e representam médias simples sem controle por tipo de produto,
região ou período.
</p>

<div class="nota-metodologica">
<strong>Nota metodológica:</strong>
a separação em duas etapas depende da disponibilidade de
<code>order_delivered_carrier_date</code>. Pedidos sem essa data foram
excluídos desta análise. A comparação não indica responsabilidade causal
de nenhum agente; ela identifica onde o tempo está associado a maior duração
na média observada.
</div>

{figura_html(grafico_gargalo, 3, "Gargalo logístico: tempo médio por etapa em pedidos atrasados")}

<h3 id="sazonalidade-risco">3.5 Sazonalidade da receita em risco</h3>

<p>
A evolução mensal da receita associada ao risco indica períodos de maior
concentração. O destaque para novembro de 2017 a fevereiro de 2018 coincide
com a Black Friday de 2017 e com as festas de fim de ano.
</p>

<p>
A concentração de risco nesse período pode estar associada ao aumento do
volume de pedidos, a limitações de capacidade logística em períodos de pico,
ou a ambos os fatores. A atribuição causal exige comparação com o mesmo
período em anos anteriores e controle do volume total de pedidos por mês.
</p>

<div class="nota-metodologica">
<strong>Nota metodológica:</strong>
o pico sazonal não pode ser interpretado como evidência direta de que a
Black Friday ou o Natal causaram os atrasos. A sobreposição temporal é
indicativa, não conclusiva.
</div>

{figura_html(grafico_sazonalidade, 4, "Sazonalidade da receita em risco com destaque para pico sazonal")}

<h3 id="peso-frete-atraso">3.6 Relação entre peso do produto, frete e atraso</h3>

<p>
A correlação entre o peso médio do produto e os dias de atraso foi de
<strong>{corr_peso:.2f}</strong>. A correlação entre o valor do frete e os
dias de atraso foi de <strong>{corr_frete:.2f}</strong>. Ambas as correlações
são classificadas como quase nulas, indicando que não foi observada relação
linear relevante entre essas variáveis e o atraso na base analisada.
</p>

<p>
Esse resultado sugere que o atraso não está associado a características físicas
da carga nem ao custo de frete. Esse padrão é consistente com um problema
sistêmico na capacidade operacional da malha de distribuição.
</p>

{figura_html(grafico_peso_frete, 5, "Peso médio e frete total versus dias de atraso (pedidos atrasados)")}

<h3 id="distancia-desempenho">3.7 Impacto da distância no desempenho logístico</h3>

<p>
A distância entre vendedor e comprador foi estimada pela fórmula de Haversine,
usando as coordenadas médias por prefixo de CEP. A análise preservou a
granularidade de um pedido por linha, selecionando o primeiro vendedor listado
nos itens de cada pedido. Os pedidos foram agrupados em cinco faixas de
distância para comparar o tempo médio de transporte e a taxa de atraso.
</p>

<p>
A correlação entre distância e dias de atraso foi de
<strong>{correlacao_distancia:.2f}</strong>, classificada como quase nula.
Esse resultado sugere que a quilometragem percorrida não está associada de
forma linear ao atraso observado na base. O padrão é consistente com um
problema logístico sistêmico, não fundamentalmente geográfico.
</p>

<div class="nota-metodologica">
<strong>Nota metodológica:</strong>
a distância foi calculada em linha reta a partir do centroide do prefixo de CEP,
o que não corresponde à distância real percorrida pelo transportador.
<strong>{pedidos_excluidos_distancia:,}</strong> pedido(s) foram excluídos
desta análise por não possuírem correspondência na tabela de geolocalização.
</div>

{figura_html(grafico_distancia, 6, "Distância vs. desempenho logístico: tempo de transporte e taxa de atraso por faixa")}

<h3 id="distribuicao-avaliacoes">3.8 Distribuição mensal de avaliações</h3>

<p>
O gráfico de barras empilhadas apresenta a distribuição percentual das
avaliações por mês, permitindo visualizar a evolução da proporção de notas
boas e ruins ao longo do período analisado. Cada barra soma 100%,
representando a composição das avaliações de cada mês.
</p>

<p>
A variação observada mês a mês reflete tanto mudanças na experiência do
cliente quanto o volume reduzido de pedidos no início da operação, que pode
tornar os percentuais mensais menos estáveis.
</p>

{figura_html(grafico_dist_mensal, 7, "Distribuição mensal percentual de avaliações (2016–2018)")}

<h3 id="perfil-cliente">3.9 Perfil do cliente observado</h3>

<p>
A segmentação entre novo cliente e cliente recorrente observado foi construída
com base na quantidade de pedidos.
Clientes com mais de um pedido foram classificados como recorrentes observados.
</p>

<p>
Essa classificação não equivale a uma segmentação por fidelização comprovada,
pois não considera margem, frequência mensal, ticket médio, tempo entre compras
ou valor de vida do cliente. A classificação não controla a janela temporal:
clientes que realizaram a primeira compra próxima ao fim do período analisado
tiveram menos oportunidade de realizar uma segunda compra.
</p>

{figura_html(grafico_perfil, 8, "Receita associada ao risco por perfil de cliente observado")}

<h3 id="retencao-exploratoria">3.10 Retenção exploratória após a primeira experiência</h3>

<p>
A recompra foi aproximada pela existência de mais de um pedido para o mesmo
cliente único na base histórica. Essa medida é exploratória e não controla
a janela de observação. Clientes que compraram no final do período tiveram
menos tempo disponível para realizar uma nova compra, o que pode subestimar
as taxas de retorno reais.
</p>

{figura_html(grafico_retorno, 9, "Retorno observado segundo a avaliação da primeira experiência")}

<h2 id="recomendacoes">4 Recomendações executivas</h2>

<ol>
<li>
<strong>Priorizar a investigação dos pedidos atrasados com notas baixas.</strong>
Esse grupo combina uma falha operacional observada com uma experiência negativa
do cliente.
</li>

<li>
<strong>Monitorar a mediana e o percentil 90 do prazo.</strong>
A média isolada pode esconder instabilidade e valores extremos.
</li>

<li>
<strong>Separar risco absoluto de risco relativo por estado.</strong>
Estados com maior faturamento podem apresentar maior risco absoluto apenas por
terem maior volume de pedidos.
</li>

<li>
<strong>Construir uma análise de coorte para recompra.</strong>
A comparação deve considerar clientes cuja primeira compra ocorreu em períodos
semelhantes e uma janela fixa de acompanhamento.
</li>

<li>
<strong>Investigar rotas, vendedores e etapas logísticas.</strong>
O relatório identifica associações; a identificação da causa operacional exige
análises adicionais por vendedor, região, prazo prometido, etapa de postagem e
transporte.
</li>

<li>
<strong>Evitar o uso do termo ROI.</strong>
Para calcular ROI seriam necessários os custos das ações corretivas e o retorno
financeiro incremental obtido após a intervenção.
</li>
</ol>

<h2 id="limitacoes">5 Limitações</h2>

<ul>
<li>
A base representa um período histórico específico e não necessariamente o
cenário atual da operação.
</li>

<li>
Pedidos sem data de entrega foram excluídos da análise de atraso, podendo
introduzir viés de seleção.
</li>

<li>
Correlação e associação não comprovam causalidade.
</li>

<li>
Não foram identificados custos de intervenção logística, portanto não foi
calculado ROI.
</li>

<li>
A recompra não foi analisada por coorte ou janela temporal fixa.
</li>

<li>
Outliers foram identificados, mas não excluídos automaticamente.
</li>

<li>
A distância entre vendedor e comprador foi calculada em linha reta pela
fórmula de Haversine, a partir do centroide do prefixo de CEP. Essa
estimativa não representa a distância real percorrida pelo transportador.
</li>

<li>
Pedidos sem correspondência na tabela de geolocalização foram excluídos
da análise de distância, o que pode introduzir viés geográfico nos resultados
dessa seção específica.
</li>

<li>
A existência de maior receita em risco em um estado não significa,
necessariamente, que esse estado tenha a pior performance relativa.
</li>
</ul>

<h2 id="conclusao">6 Conclusão</h2>

<p>
A análise indica uma associação relevante entre atraso na entrega e redução da
avaliação média dos pedidos. Também foi possível identificar uma exposição
financeira associada a pedidos atrasados que receberam avaliações baixas.
</p>

<p>
Os resultados sugerem que a eficiência logística deve ser tratada como uma
dimensão estratégica da experiência do cliente e da proteção da receita. No
entanto, as evidências apresentadas são descritivas e observacionais. Portanto,
a recomendação é utilizar o relatório como instrumento de priorização e
diagnóstico, e não como prova definitiva de causalidade ou previsão de
faturamento futuro.
</p>

<p>
Para fortalecer a tomada de decisão, a próxima etapa deve incluir análises de
coorte, segmentação por vendedor e rota, controle de sazonalidade, comparação
de taxas relativas e, quando possível, um teste-piloto de intervenção logística.
</p>

<h2 id="referencias">Referências</h2>

<p class="referencia">
OLIST. <strong>Brazilian E-Commerce Public Dataset by Olist</strong>.
Conjunto de dados utilizado na análise. Disponível em repositório público.
Acesso em: {datetime.now().strftime("%d %b. %Y")}.
</p>

<p class="referencia">
POSTECH. <strong>Estatística Essencial para Analytics: Aula 1 —
Papel da estatística na análise de dados e na tomada de decisão</strong>.
Material didático da disciplina. 2025.
</p>

<p class="referencia">
POSTECH. <strong>Estatística Essencial para Analytics: Aula 2 —
Tipos de variáveis e escalas de medição</strong>.
Material didático da disciplina. 2025.
</p>

<p class="referencia">
POSTECH. <strong>Estatística Essencial para Analytics: Aula 3 —
População, amostra e amostragem</strong>.
Material didático da disciplina. 2025.
</p>

<p class="referencia">
POSTECH. <strong>Estatística Essencial para Analytics: Aula 4 —
Medidas de tendência central</strong>.
Material didático da disciplina. 2025.
</p>

<p class="referencia">
POSTECH. <strong>Estatística Essencial para Analytics: Aula 5 —
Medidas de dispersão</strong>.
Material didático da disciplina. 2026.
</p>

<p class="referencia">
POSTECH. <strong>Estatística Essencial para Analytics: Aula 6 —
Identificação de outliers e distribuição dos dados</strong>.
Material didático da disciplina. 2025.
</p>

<p style="font-size: 10pt; margin-top: 30px;">
Relatório gerado em {data_geracao}.
</p>

</body>
</html>
"""

caminho_html = REPORT_DIR / "relatorio_executivo.html"

with open(caminho_html, "w", encoding="utf-8") as arquivo:
    arquivo.write(html_relatorio)

print(f"\nRelatório HTML gerado em: {caminho_html}")
# %%
caminho_pdf = REPORT_DIR / "relatorio_executivo.pdf"

HTML(filename=str(caminho_html), base_url=str(REPORT_DIR)).write_pdf(str(caminho_pdf))

print(f"PDF gerado em: {caminho_pdf}")
