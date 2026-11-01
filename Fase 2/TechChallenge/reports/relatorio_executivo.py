from __future__ import annotations

import json
from pathlib import Path

from weasyprint import HTML

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
REPORTS_DIR = Path(__file__).resolve().parent

PARTICIPANTS = [
    "Julia Ayumi Suzuki",
    "Larissa Nicoli Rodrigues",
    "Matheus Silva de Jesus",
    "Paulo Jean Alves da Silva",
]


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def fmt_metric(value):
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:.4f}"
    return str(value)


def build_table(rows, headers):
    ths = "".join(f"<th>{header}</th>" for header in headers)
    trs = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"""
    <table class="table">
      <thead><tr>{ths}</tr></thead>
      <tbody>{trs}</tbody>
    </table>
    """


NOTEBOOK_VISUAL_EXPLANATIONS = {
    "01_eda.ipynb": [
        "A história começa com um ponto central: a classe positiva é minoritária, então o problema exige foco em métricas de equilíbrio e sensibilidade, e não apenas acurácia.",
        "Em seguida, a distribuição da qualidade mostra como as classes se organizam no conjunto e justifica por que a fronteira de decisão não é trivial.",
        "A proporção entre classes reforça o contexto de desbalanceamento observado na etapa inicial.",
        "A matriz de correlação mostra que a qualidade não responde a um único fator isolado, mas à combinação entre variáveis físico-químicas.",
        "A separação do teor alcoólico por classe fortalece a leitura de que algumas variáveis carregam sinal preditivo relevante.",
        "Por fim, os boxplots com IQR revelam caudas e extremos importantes, orientando a etapa de validação de outliers sem alterar prematuramente o conjunto.",
    ],
    "02_modelo_e_validacao.ipynb": [
        "A divisão estratificada entre treino e validação preserva a proporção da classe alvo e reduz risco de vazamento de informação.",
        "A comparação entre modelos mostra que a acurácia isolada não é suficiente quando a classe positiva é minoritária.",
        "O equilíbrio entre recall e precision é central para a decisão, especialmente na classe relevante do problema.",
        "A validação interna reforça que o desempenho deve ser medido em conjunto, e não por uma única métrica isolada.",
        "Os resultados apontam que o Random Forest e o HistGradientBoosting são os modelos mais competitivos, com diferenças definidas pelo trade-off de negócio.",
        "A comparação final sustenta a decisão por equilíbrio geral e pela avaliação no conjunto de teste reservado.",
    ],
    "03_regressao_linear.ipynb": [
        "A regressão linear não captura de forma suficiente a relação entre variáveis e a qualidade do vinho.",
        "Os resíduos sugerem que o padrão é mais complexo e exige modelos não lineares para uma melhor separação da classe alvo.",
        "Esse diagnóstico confirma que a regressão linear funciona como referência, mas não como solução principal do problema.",
    ],
    "04_train_test_split.ipynb": [
        "A separação entre treino e teste preserva a capacidade de generalização e evita decisões baseadas em overfitting.",
        "A comparação em dados não vistos é a base mais confiável para a recomendação final.",
    ],
    "05_validacao_cruzada.ipynb": [
        "A validação cruzada mostra que o desempenho se mantém estável em diferentes subconjuntos do dado, reduzindo o impacto de uma divisão favorável."
    ],
    "06_clusterizacao.ipynb": [
        "A clusterização não explica diretamente a classe alvo e, por isso, não substitui a modelagem supervisionada."
    ],
    "07_arvore_decisao_pm.ipynb": [
        "A árvore aumenta a interpretabilidade do modelo e ajuda a explicar regras de decisão.",
        "Mesmo com boa explicabilidade, ela não supera a melhor performance global dos modelos de ensemble.",
    ],
}


def build_notebook_section(
    nb_name: str,
    title: str,
    show_section_title: bool = True,
    force_break_before: bool = True,
):
    nb_path = ROOT_DIR / "notebooks" / nb_name
    with nb_path.open("r", encoding="utf-8") as fh:
        notebook = json.load(fh)

    images = []
    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            data = output.get("data", {})
            if "image/png" not in data:
                continue
            image_b64 = data["image/png"]
            if isinstance(image_b64, list):
                image_b64 = "".join(str(item) for item in image_b64)
            images.append(image_b64)

    explanations = NOTEBOOK_VISUAL_EXPLANATIONS.get(nb_name, [])
    section_classes = ["notebook-section"]
    if force_break_before and nb_name == "03_regressao_linear.ipynb":
        section_classes.append("notebook-break-before")

    part_html = [f"<section class=\"{' '.join(section_classes)}\">"]
    if show_section_title:
        part_html.append(f"<h3>{title}</h3>")

    for index, image_b64 in enumerate(images, start=1):
        explanation = (
            explanations[index - 1]
            if index - 1 < len(explanations)
            else "Este gráfico reforça a conclusão analítica do notebook e sustenta a interpretação do modelo."
        )

        graph_classes = ["graph-block"]
        if nb_name == "01_eda.ipynb" and index in {1, 2, 3, 4}:
            graph_classes.append("graph-compact")
        if nb_name == "01_eda.ipynb" and index == 6:
            graph_classes.append("graph-outlier-large")
        if nb_name == "02_modelo_e_validacao.ipynb" and index in {3, 4, 5, 6}:
            graph_classes.append("graph-compact")
        if nb_name in {"05_validacao_cruzada.ipynb", "06_clusterizacao.ipynb"}:
            graph_classes.append("graph-compact")

        if (nb_name == "01_eda.ipynb" and index in {1, 3}) or (
            nb_name == "02_modelo_e_validacao.ipynb" and index in {1, 3, 5}
        ):
            part_html.append('<div class="graph-pair">')

        part_html.append(f"""
            <div class="{' '.join(graph_classes)}">
              <figure>
                <img src="data:image/png;base64,{image_b64}" alt="{title} - gráfico {index}" />
                <figcaption>{title} — Gráfico {index}</figcaption>
              </figure>
              <p class="img-explain">{explanation}</p>
            </div>
            """)

        if (nb_name == "01_eda.ipynb" and index in {2, 4}) or (
            nb_name == "02_modelo_e_validacao.ipynb" and index in {2, 4, 6}
        ):
            part_html.append("</div>")

    part_html.append("</section>")
    return "".join(part_html)


def build_notebook_sections_html(
    notebook_order=None,
    show_section_titles: bool = True,
    force_break_before: bool = True,
):
    if notebook_order is None:
        notebook_order = [
            ("01_eda.ipynb", "Análise exploratória e entendimento do problema"),
            ("02_modelo_e_validacao.ipynb", "Modelagem, comparação e decisão final"),
            ("03_regressao_linear.ipynb", "Regressão Linear"),
            ("04_train_test_split.ipynb", "Train/Test Split"),
            ("05_validacao_cruzada.ipynb", "Validação Cruzada"),
            ("06_clusterizacao.ipynb", "Clusterização"),
            ("07_arvore_decisao_pm.ipynb", "Árvore de decisão"),
        ]

    parts = []
    for nb_name, title in notebook_order:
        if nb_name == "05_validacao_cruzada.ipynb":
            parts.append('<div class="cv-cluster-group">')
        parts.append(
            build_notebook_section(
                nb_name,
                title,
                show_section_title=show_section_titles,
                force_break_before=force_break_before,
            )
        )
        if nb_name == "06_clusterizacao.ipynb":
            parts.append("</div>")
    return "".join(parts)


def build_validation_rows(metrics):
    order = [
        ("baseline_majority", "Baseline majoritário"),
        ("logreg_balanced", "Logistic Regression (balanced)"),
        ("random_forest_balanced", "Random Forest (balanced)"),
        ("hist_gb", "HistGradientBoosting"),
    ]
    rows = []
    for key, label in order:
        item = metrics[key]
        rows.append(
            [
                label,
                fmt_metric(item["accuracy"]),
                fmt_metric(item["precision"]),
                fmt_metric(item["recall"]),
                fmt_metric(item["f1"]),
                fmt_metric(item["roc_auc"]),
                fmt_metric(item["average_precision"]),
            ]
        )
    return rows


def build_test_rows(metrics):
    order = [
        ("baseline_majority", "Baseline majoritário"),
        ("random_forest_balanced", "Random Forest (balanced)"),
        ("hist_gb", "HistGradientBoosting"),
    ]
    rows = []
    for key, label in order:
        item = metrics[key]
        rows.append(
            [
                label,
                fmt_metric(item["accuracy"]),
                fmt_metric(item["precision"]),
                fmt_metric(item["recall"]),
                fmt_metric(item["f1"]),
                fmt_metric(item["roc_auc"]),
                fmt_metric(item["average_precision"]),
            ]
        )
    return rows


def build_threshold_rows(metrics):
    baseline = metrics["baseline_threshold_0_50"]
    best_f1 = metrics["best_threshold_by_f1"]
    tradeoff = metrics.get("high_recall_tradeoff")

    rows = [
        [
            "Baseline t=0.50",
            fmt_metric(baseline["threshold"]),
            fmt_metric(baseline["f1"]),
            fmt_metric(baseline["recall"]),
            fmt_metric(baseline["precision"]),
        ],
        [
            "Melhor F1",
            fmt_metric(best_f1["threshold"]),
            fmt_metric(best_f1["f1"]),
            fmt_metric(best_f1["recall"]),
            fmt_metric(best_f1["precision"]),
        ],
    ]

    if tradeoff is not None:
        rows.append(
            [
                "Trade-off de recall",
                fmt_metric(tradeoff["threshold"]),
                fmt_metric(tradeoff["f1"]),
                fmt_metric(tradeoff["recall"]),
                fmt_metric(tradeoff["precision"]),
            ]
        )

    return rows


def build_html():
    validation_metrics = read_json(RESULTS_DIR / "model_validation_metrics.json")
    test_metrics = read_json(RESULTS_DIR / "final_test_evaluation.json")
    threshold_metrics = read_json(RESULTS_DIR / "threshold_cv_experiment.json")
    threshold_test_metrics = read_json(RESULTS_DIR / "threshold_test_evaluation.json")

    validation_rows = build_validation_rows(validation_metrics)
    test_rows = build_test_rows(test_metrics)
    threshold_rows = build_threshold_rows(threshold_metrics)
    exploratory_sections_html = build_notebook_sections_html(
        [
            ("01_eda.ipynb", "Análise exploratória"),
        ],
        show_section_titles=False,
        force_break_before=False,
    )
    complementary_sections_html = build_notebook_sections_html(
        [
            ("02_modelo_e_validacao.ipynb", "Modelagem, comparação e decisão final"),
            ("03_regressao_linear.ipynb", "Regressão linear"),
            ("04_train_test_split.ipynb", "Train/Test Split"),
            ("05_validacao_cruzada.ipynb", "Validação cruzada"),
            ("06_clusterizacao.ipynb", "Clusterização"),
            ("07_arvore_decisao_pm.ipynb", "Árvore de decisão"),
        ],
        show_section_titles=False,
        force_break_before=False,
    )

    participants_html = "".join(f"<p>{name}</p>" for name in PARTICIPANTS)

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Relatório Executivo — WineQT</title>
  <style>
    @page {{
      size: A4;
      margin: 2.3cm 1.9cm 2.1cm 1.9cm;
      @top-left {{
        content: string(chapter-title);
        font-size: 9pt;
        color: #666;
      }}
      @bottom-right {{
        content: "Página " counter(page) " de " counter(pages);
        font-size: 9pt;
        color: #666;
      }}
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      font-family: 'Times New Roman', serif;
      font-size: 12pt;
      line-height: 1.5;
      color: #1d1d1d;
      margin: 0;
      background: #fff;
      text-align: justify;
    }}

    h1, h2, h3 {{
      font-family: 'Times New Roman', serif;
      color: #111;
      text-align: left;
      font-weight: bold;
      margin-top: 1.2em;
      margin-bottom: 0.45em;
    }}

    h1 {{
      font-size: 20pt;
      text-align: center;
      margin-top: 1.5em;
      margin-bottom: 1em;
    }}

    h2 {{
      font-size: 15pt;
      margin-top: 1.6em;
      string-set: chapter-title content(text);
      border-left: 4px solid #444;
      padding-left: 0.45em;
    }}

    h3 {{
      font-size: 13pt;
      margin-top: 1.1em;
    }}

    .capa {{
      page-break-after: always;
      text-align: center;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding-top: 0.7cm;
      padding-bottom: 0.7cm;
    }}

    .capa .titulo {{
      font-size: 18pt;
      font-weight: bold;
      margin-bottom: 0.8em;
    }}

    .capa .subtitulo {{
      font-size: 12pt;
      margin-top: 0.2em;
      margin-bottom: 0.8em;
    }}

    .capa .autores {{
      margin-top: 1.1em;
      font-size: 11pt;
      line-height: 1.2;
    }}

    .capa .autores p {{
      margin: 0.12em 0;
    }}

    .capa .rodape-capa {{
      margin-top: auto;
      font-size: 11pt;
      padding-top: 1.5em;
    }}

    .sumario {{
      page-break-after: always;
      margin-top: 1.5em;
    }}

    .sumario ol {{
      list-style: none;
      margin-top: 0.5em;
      padding-left: 0;
    }}

    .sumario li {{
      margin-bottom: 0.35em;
    }}

    .sumario a {{
      color: #111;
      text-decoration: none;
      display: block;
      font-size: 11pt;
    }}

    .sumario a::after {{
      content: leader('.') target-counter(attr(href), page);
    }}

    .sumario .toc-sub {{
      padding-left: 1.1em;
      font-size: 10.5pt;
      color: #333;
    }}

    .resumo-box {{
      border: 1px solid #555;
      padding: 0.8em 1em;
      background: #f8f8f8;
      margin: 1em 0;
    }}

    .kpis {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.75em;
      margin: 1.3em 0 1.8em 0;
    }}

    .kpi {{
      border: 1px solid #bdbdbd;
      background: #fafafa;
      padding: 0.7em 0.8em;
      text-align: center;
    }}

    .kpi strong {{
      display: block;
      font-size: 16pt;
      margin-bottom: 0.2em;
    }}

    .table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1em 0 1.2em 0;
      font-size: 10pt;
    }}

    .table th, .table td {{
      border: 1px solid #444;
      padding: 0.4em 0.45em;
      text-align: center;
      vertical-align: middle;
    }}

    .table th {{
      background: #eeeeee;
      font-weight: bold;
    }}

    figure {{
      margin: 1.3em 0 1.8em 0;
      text-align: center;
      page-break-inside: avoid;
    }}

    figure img {{
      max-width: 100%;
      height: auto;
      max-height: 12.8cm;
      border: 1px solid #ddd;
      display: block;
      margin: 0 auto;
    }}

    .graph-block {{
      page-break-inside: avoid;
      break-inside: avoid;
      margin: 0 0 0.85em 0;
    }}

    .graph-compact figure img {{
      max-height: 8.2cm;
    }}

    .graph-outlier-large figure img {{
      max-height: 22cm;
      width: 100%;
      object-fit: contain;
    }}

    .graph-pair {{
      display: block;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    .graph-pair .graph-block + .graph-block {{
      margin-top: 0.4em;
    }}

    .notebook-section {{
      page-break-inside: auto;
      break-inside: auto;
    }}

    .notebook-break-before {{
      page-break-before: always;
      break-before: page;
    }}

    .cv-cluster-group {{
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    figcaption {{
      margin-top: 0.5em;
      font-size: 9pt;
      text-align: center;
      color: #333;
    }}

    ul, ol {{
      padding-left: 1.4em;
    }}

    .note {{
      background: #f5f5f5;
      border-left: 4px solid #555;
      padding: 0.8em 1em;
      margin: 1em 0;
    }}

    .img-explain {{
      margin-top: -0.5em;
      margin-bottom: 0.55em;
      font-size: 10.5pt;
      line-height: 1.5;
      text-align: justify;
    }}

    .compact-lead {{
      margin-top: 0.3em;
      margin-bottom: 0.45em;
    }}

    .complementary-flow .notebook-section {{
      margin-top: 0.2em;
    }}

    .story-intro {{
      background: #f7f7f7;
      border-left: 4px solid #444;
      padding: 0.75em 0.95em;
      margin: 0.8em 0 1em 0;
    }}

    .footer {{
      margin-top: 2em;
      font-size: 10pt;
      text-align: center;
      color: #444;
    }}

    .section-break {{
      page-break-before: always;
    }}
  </style>
</head>
<body>
  <section class="capa">
    <div class="titulo">RELATÓRIO EXECUTIVO</div>
    <div class="subtitulo">DATA ANALYTICS — FIAP</div>
    <div class="subtitulo">WineQT — Classificação de qualidade de vinho</div>
    <div class="autores">
      {participants_html}
    </div>
    <div class="rodape-capa">São Paulo — 2026</div>
  </section>

  <section class="sumario">
    <h2 id="sumario">Sumário</h2>
    <ol>
      <li><a href="#resumo-executivo">1. Resumo executivo</a></li>
      <li><a href="#objetivos">2. Objetivos</a></li>
      <li><a href="#metodologia-notebooks">3. Metodologia e evidência dos notebooks</a></li>
      <li><a href="#diagnostico-exploratorio">4. Diagnóstico exploratório</a></li>
      <li class="toc-sub"><a href="#analise-exploratoria-sub">4.1 Análise exploratória</a></li>
      <li class="toc-sub"><a href="#evidencias-complementares-sub">4.2 Evidências complementares</a></li>
      <li><a href="#resultados-validacao">5. Resultados de validação</a></li>
      <li class="toc-sub"><a href="#ajuste-limiar">5.1 Ajuste de limiar</a></li>
      <li class="toc-sub"><a href="#checagem-teste-limiar">5.2 Checagem final no teste reservado</a></li>
      <li><a href="#avaliacao-teste">6. Avaliação final no teste reservado</a></li>
      <li><a href="#conclusao-final">7. Conclusão final</a></li>
    </ol>
  </section>

  <h2 id="resumo-executivo">1. Resumo executivo</h2>
  <div class="resumo-box">
    <p>
      O projeto partiu de uma pergunta objetiva: como identificar, de forma confiável, vinhos de alta qualidade usando apenas atributos físico-químicos.
      A regra de negócio foi mantida do início ao fim: <strong>quality &ge; 7</strong> como classe positiva e <strong>quality &lt; 7</strong> como classe negativa.
      Como a classe positiva é minoritária, a análise foi conduzida com foco em equilíbrio entre sensibilidade e precisão da classe relevante.
    </p>
    <p>
      Na trilha de decisão, comparamos modelos, validamos alternativas para outliers e calibramos limiar sem usar o teste final na escolha.
      O desfecho foi a recomendação de <strong>Random Forest com balanceamento de classes</strong> e limiar operacional de <strong>0.46</strong>,
      sustentado por <strong>F1, recall, precision, ROC-AUC e Average Precision</strong>.
    </p>
  </div>

  <div class="kpis">
    <div class="kpi"><strong>0.6647</strong>F1 do Random Forest com limiar 0.46 (CV)</div>
    <div class="kpi"><strong>0.4167</strong>F1 do Random Forest com limiar 0.46 (teste)</div>
    <div class="kpi"><strong>0.4167</strong>Recall do Random Forest com limiar 0.46 (teste)</div>
  </div>

  <h2 id="objetivos">2. Objetivos</h2>
  <h3>Objetivo geral</h3>
  <p>
    Construir e validar um modelo preditivo capaz de identificar vinhos de alta qualidade a partir de atributos físico-químicos,
    com rigor metodológico e métricas adequadas ao desbalanceamento de classes.
  </p>

  <h3>Objetivos específicos</h3>
  <ul>
    <li>confirmar a definição da variável alvo binária;</li>
    <li>validar a separação entre treino, validação e teste sem leakage;</li>
    <li>comparar modelos com foco na classe minoritária;</li>
    <li>interpretar resultados dos notebooks de regressão, split, validação cruzada, clusterização e árvore de decisão;</li>
    <li>definir a recomendação final com base em evidência e não em suposição.</li>
  </ul>

  <h2 id="metodologia-notebooks">3. Metodologia e evidência dos notebooks</h2>
  <h3>Objetivo da análise</h3>
  <p>
    A trilha metodológica foi montada como uma sequência de decisão: entender o dado, testar alternativas em ambiente controlado e validar a decisão final em conjunto reservado.
    Como o problema é desbalanceado, o foco permaneceu na classe positiva durante todas as comparações.
  </p>

  <h3>Evidência dos notebooks</h3>
  <p>
    A análise exploratória mostrou que a classe de alta qualidade representa cerca de 13,9% do conjunto.
    Esse ponto definiu a régua analítica: F1, recall e ROC-AUC ganharam prioridade sobre acurácia isolada.
    Também foi observado que álcool e correlações multivariadas oferecem sinal útil para distinguir as classes.
  </p>
  <p>
    Na etapa de outliers, boxplots e critério de IQR destacaram extremos em sulfur dioxide, chlorides e residual sugar.
    A decisão foi não remover pontos de forma automática no EDA, preservando sinal potencial da classe positiva para avaliação experimental posterior.
  </p>

  <h3>Decisão metodológica</h3>
  <p>
    Os testes mostraram que regressão linear funciona como referência, mas não captura a complexidade do problema.
    A divisão estratificada e a validação cruzada trouxeram estabilidade para a comparação.
    A árvore de decisão contribuiu para explicabilidade, enquanto os ensembles sustentaram melhor desempenho preditivo.
  </p>

  <div class="note">
    A coluna <strong>Id</strong> foi excluída dos preditores, em conformidade com o enunciado, e o preprocessamento foi ajustado apenas sobre os dados de treino.
  </div>

  <ul>
    <li><strong>Regressão Linear</strong>: não foi suficiente para explicar a qualidade de forma robusta; o padrão é mais complexo e exige modelos não lineares.</li>
    <li><strong>Train/Test Split</strong>: preservou a proporção da classe alvo e reduziu o risco de vazamento entre etapas.</li>
    <li><strong>Validação Cruzada</strong>: reforçou a estabilidade do desempenho e reduziu a chance de decisão baseada em uma divisão favorável.</li>
    <li><strong>Clusterização</strong>: foi útil como diagnóstico, mas não como solução principal para a classificação alvo.</li>
    <li><strong>Árvore de decisão</strong>: ajudou na interpretação das regras, mas não superou o melhor ensemble no teste final.</li>
  </ul>

  <h2 id="diagnostico-exploratorio">4. Diagnóstico exploratório</h2>
  <div class="story-intro">
    A leitura exploratória abre a narrativa do projeto: primeiro entendemos a distribuição da classe e da qualidade, depois avaliamos relações entre variáveis e, por fim, diagnosticamos outliers. Isso prepara o terreno para a modelagem com critérios claros de decisão.
  </div>

  <h3 id="analise-exploratoria-sub">4.1 Análise exploratória</h3>
  <p>
    Esta seção apresenta os sinais iniciais do problema: distribuição da classe alvo, distribuição da qualidade, relações entre variáveis e diagnóstico de outliers. O objetivo é contextualizar por que as etapas seguintes priorizam métricas de equilíbrio da classe positiva.
  </p>
  {exploratory_sections_html}

  <h3 id="evidencias-complementares-sub">4.2 Evidências complementares da trilha analítica</h3>
  <p class="compact-lead">
    Com a base exploratória consolidada, a sequência abaixo mostra como cada etapa complementar sustentou a recomendação final, preservando separação entre treino, validação e teste.
  </p>
  <div class="complementary-flow">{complementary_sections_html}</div>

  <h2 id="resultados-validacao" class="section-break">5. Resultados de validação</h2>
  <figure>
    <img src="figures/model_f1_comparison.png" alt="Comparação de F1 por modelo" />
    <figcaption>Figura 4 — Comparação de F1 por modelo na validação.</figcaption>
  </figure>

  {build_table(validation_rows, ['Modelo', 'Acurácia', 'Precision', 'Recall', 'F1', 'ROC-AUC', 'Average Precision'])}

  <p>A performance de validação mostra que:</p>
  <ul>
    <li>o <strong>HistGradientBoosting</strong> apresentou o melhor F1 (0,6667) e precision (0,7600) na etapa de validação;</li>
    <li>o <strong>Random Forest balanceado</strong> ficou muito próximo, com F1 de 0,6563 e ROC-AUC de 0,9408;</li>
    <li>a <strong>Logistic Regression</strong> teve maior recall, mas pior equilíbrio geral e pior precision;</li>
    <li>o <strong>baseline majoritário</strong> não é competitivo e serve apenas como referência.</li>
  </ul>

  <h3 id="ajuste-limiar" class="section-break">Ajuste de limiar</h3>
  <p>
    Após escolher o modelo baseline, foi feito ajuste de limiar usando apenas validação cruzada estratificada.
    O objetivo foi deixar claro o trade-off entre recall e precision da classe positiva.
  </p>

  {build_table(threshold_rows, ['Cenário', 'Limiar', 'F1', 'Recall', 'Precision'])}

  <p>
    A recomendação operacional padrão é <strong>limiar 0.46</strong>, por melhor F1 médio na validação.
    Se a prioridade for aumentar sensibilidade da classe positiva, o cenário em <strong>0.42</strong> aumenta recall,
    com queda de precision.
  </p>

  <h3 id="checagem-teste-limiar">Checagem final no teste reservado</h3>
  <p>
    A comparação final confirmou que, para o Random Forest, o limiar 0.46 melhorou F1 e recall em relação ao limiar 0.50,
    com pequena queda de acurácia.
  </p>

  {build_table([
    ['t=0.50', fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_5']['accuracy']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_5']['precision']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_5']['recall']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_5']['f1'])],
    ['t=0.46', fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_46']['accuracy']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_46']['precision']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_46']['recall']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_46']['f1'])],
    ['t=0.42', fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_42']['accuracy']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_42']['precision']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_42']['recall']), fmt_metric(threshold_test_metrics['threshold_metrics']['t_0_42']['f1'])],
  ], ['Limiar', 'Acurácia', 'Precision', 'Recall', 'F1'])}

  <h2 id="avaliacao-teste" class="section-break">6. Avaliação final no teste reservado</h2>
  <figure>
    <img src="figures/final_model_comparison.png" alt="Comparação final no conjunto de teste" />
    <figcaption>Figura 5 — Comparação final no conjunto de teste.</figcaption>
  </figure>

  <p>
    O conjunto de teste reservado foi a etapa decisiva. O Random Forest balanceado ficou como principal por manter melhor equilíbrio entre F1 e recall da classe positiva.
    O HistGradientBoosting manteve boa precision, mas com recall menor.
  </p>

  {build_table(test_rows, ['Modelo', 'Acurácia', 'Precision', 'Recall', 'F1', 'ROC-AUC', 'Average Precision'])}

  <p>
    Em termos práticos, o <strong>Random Forest</strong> teve melhor equilíbrio para este problema desbalanceado.
    O <strong>HistGradientBoosting</strong> segue como alternativa quando a prioridade for precision.
  </p>

  <h2 id="conclusao-final" class="section-break">7. Conclusão final</h2>
  <p>A recomendação final do projeto é:</p>
  <ul>
    <li><strong>Random Forest balanced</strong> como modelo principal;</li>
    <li><strong>limiar 0.46</strong> como configuração padrão de classificação;</li>
    <li><strong>limiar 0.42</strong> como alternativa quando a meta for maior recall;</li>
    <li><strong>HistGradientBoosting</strong> como alternativa preferencial quando a organização prioriza precision;</li>
    <li><strong>regressão linear</strong> e <strong>clusterização</strong> como diagnósticos e ferramentas complementares, mas não como solução principal;</li>
    <li><strong>árvore de decisão</strong> como apoio interpretativo, não como substituta da melhor performance global.</li>
  </ul>
  <p>
    Em síntese, a decisão foi guiada por evidência de validação e teste reservado.
    O projeto fecha com modelo definido e política de limiar clara para diferentes objetivos de negócio.
  </p>

  <div class="footer">
    Relatório executado com base nos resultados finais do WineQT e nos notebooks gerados no projeto.
  </div>
</body>
</html>
"""

    return html


def main():
    html_content = build_html()
    html_path = REPORTS_DIR / "relatorio_executivo.html"
    pdf_path = REPORTS_DIR / "relatorio_executivo.pdf"

    html_path.write_text(html_content, encoding="utf-8")

    HTML(string=html_content, base_url=str(REPORTS_DIR)).write_pdf(str(pdf_path))
    print(f"HTML salvo em: {html_path}")
    print(f"PDF salvo em: {pdf_path}")


if __name__ == "__main__":
    main()
