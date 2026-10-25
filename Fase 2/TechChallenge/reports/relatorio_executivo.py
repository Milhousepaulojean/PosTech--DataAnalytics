from __future__ import annotations

import base64
import json
from pathlib import Path

from weasyprint import HTML

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / 'results'
REPORTS_DIR = Path(__file__).resolve().parent

PARTICIPANTS = [
    'Julia Ayumi Suzuki',
    'Larissa Nicoli Rodrigues',
    'Matheus Silva de Jesus',
    'Paulo Jean Alves da Silva',
]


def read_json(path: Path):
    with path.open('r', encoding='utf-8') as fh:
        return json.load(fh)


def fmt_metric(value):
    if value is None:
        return '—'
    if isinstance(value, (int, float)):
        return f'{value:.4f}'
    return str(value)


def build_table(rows, headers):
    ths = ''.join(f'<th>{header}</th>' for header in headers)
    trs = ''.join(
        '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
        for row in rows
    )
    return f'''
    <table class="table">
      <thead><tr>{ths}</tr></thead>
      <tbody>{trs}</tbody>
    </table>
    '''


NOTEBOOK_VISUAL_EXPLANATIONS = {
    '01_eda.ipynb': [
        'A distribuição da classe alvo mostra que a classe positiva é minoritária e exige avaliação por métricas orientadas à classe relevante.',
        'A correlação entre variáveis sugere que a qualidade depende de combinações de atributos, não de um único fator isolado.',
        'A separação do teor alcoólico por classe reforça o poder discriminativo da variável e a plausibilidade do problema de classificação.',
        'Os gráficos indicam sinais claros de diferença entre classes, mas também deixam evidente que o problema não é simples de uma variável isolada.',
        'Esse diagnóstico sustentou a continuidade da modelagem com técnicas mais flexíveis do que a regressão linear simples.'
    ],
    '02_modelo_e_validacao.ipynb': [
        'A divisão estratificada entre treino e validação preserva a proporção da classe alvo e reduz risco de vazamento de informação.',
        'A comparação entre modelos mostra que a acurácia isolada não é suficiente quando a classe positiva é minoritária.',
        'O equilíbrio entre recall e precision é central para a decisão, especialmente na classe relevante do problema.',
        'A validação interna reforça que o desempenho deve ser medido em conjunto, e não por uma única métrica isolada.',
        'Os resultados apontam que o Random Forest e o HistGradientBoosting são os modelos mais competitivos, com diferenças definidas pelo trade-off de negócio.',
        'A comparação final sustenta a decisão por equilíbrio geral e pela avaliação no conjunto de teste reservado.'
    ],
    '03_regressao_linear.ipynb': [
        'A regressão linear não captura de forma suficiente a relação entre variáveis e a qualidade do vinho.',
        'Os resíduos sugerem que o padrão é mais complexo e exige modelos não lineares para uma melhor separação da classe alvo.',
        'Esse diagnóstico confirma que a regressão linear funciona como referência, mas não como solução principal do problema.'
    ],
    '04_train_test_split.ipynb': [
        'A separação entre treino e teste preserva a capacidade de generalização e evita decisões baseadas em overfitting.',
        'A comparação em dados não vistos é a base mais confiável para a recomendação final.'
    ],
    '05_validacao_cruzada.ipynb': [
        'A validação cruzada mostra que o desempenho se mantém estável em diferentes subconjuntos do dado, reduzindo o impacto de uma divisão favorável.'
    ],
    '06_clusterizacao.ipynb': [
        'A clusterização não explica diretamente a classe alvo e, por isso, não substitui a modelagem supervisionada.'
    ],
    '07_arvore_decisao_pm.ipynb': [
        'A árvore aumenta a interpretabilidade do modelo e ajuda a explicar regras de decisão.',
        'Mesmo com boa explicabilidade, ela não supera a melhor performance global dos modelos de ensemble.'
    ],
}


def build_notebook_section(nb_name: str, title: str):
    nb_path = ROOT_DIR / 'notebooks' / nb_name
    with nb_path.open('r', encoding='utf-8') as fh:
        notebook = json.load(fh)

    images = []
    for cell in notebook.get('cells', []):
        for output in cell.get('outputs', []):
            data = output.get('data', {})
            if 'image/png' not in data:
                continue
            image_b64 = data['image/png']
            if isinstance(image_b64, list):
                image_b64 = ''.join(str(item) for item in image_b64)
            images.append(image_b64)

    explanations = NOTEBOOK_VISUAL_EXPLANATIONS.get(nb_name, [])
    part_html = [f'<h3>{title}</h3>']
    for index, image_b64 in enumerate(images, start=1):
        explanation = explanations[index - 1] if index - 1 < len(explanations) else 'Este gráfico reforça a conclusão analítica do notebook e sustenta a interpretação do modelo.'
        part_html.append(
            f'''
            <figure>
              <img src="data:image/png;base64,{image_b64}" alt="{title} - gráfico {index}" />
              <figcaption>{title} — Gráfico {index}</figcaption>
            </figure>
            <p class="img-explain">{explanation}</p>
            '''
        )
    return ''.join(part_html)


def build_notebook_sections_html():
    notebook_order = [
        ('01_eda.ipynb', 'Análise exploratória e entendimento do problema'),
        ('02_modelo_e_validacao.ipynb', 'Modelagem, comparação e decisão final'),
        ('03_regressao_linear.ipynb', 'Regressão Linear'),
        ('04_train_test_split.ipynb', 'Train/Test Split'),
        ('05_validacao_cruzada.ipynb', 'Validação Cruzada'),
        ('06_clusterizacao.ipynb', 'Clusterização'),
        ('07_arvore_decisao_pm.ipynb', 'Árvore de decisão'),
    ]
    return ''.join(build_notebook_section(nb_name, title) for nb_name, title in notebook_order)


def build_validation_rows(metrics):
    order = [
        ('baseline_majority', 'Baseline majoritário'),
        ('logreg_balanced', 'Logistic Regression (balanced)'),
        ('random_forest_balanced', 'Random Forest (balanced)'),
        ('hist_gb', 'HistGradientBoosting'),
    ]
    rows = []
    for key, label in order:
        item = metrics[key]
        rows.append([
            label,
            fmt_metric(item['accuracy']),
            fmt_metric(item['precision']),
            fmt_metric(item['recall']),
            fmt_metric(item['f1']),
            fmt_metric(item['roc_auc']),
            fmt_metric(item['average_precision']),
        ])
    return rows


def build_test_rows(metrics):
    order = [
        ('baseline_majority', 'Baseline majoritário'),
        ('random_forest_balanced', 'Random Forest (balanced)'),
        ('hist_gb', 'HistGradientBoosting'),
    ]
    rows = []
    for key, label in order:
        item = metrics[key]
        rows.append([
            label,
            fmt_metric(item['accuracy']),
            fmt_metric(item['precision']),
            fmt_metric(item['recall']),
            fmt_metric(item['f1']),
            fmt_metric(item['roc_auc']),
            fmt_metric(item['average_precision']),
        ])
    return rows


def build_html():
    validation_metrics = read_json(RESULTS_DIR / 'model_validation_metrics.json')
    test_metrics = read_json(RESULTS_DIR / 'final_test_evaluation.json')

    validation_rows = build_validation_rows(validation_metrics)
    test_rows = build_test_rows(test_metrics)
    notebook_sections_html = build_notebook_sections_html()

    participants_html = ''.join(f'<p>{name}</p>' for name in PARTICIPANTS)

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
      margin-top: 0.5em;
      padding-left: 1.3em;
    }}

    .sumario li {{
      margin-bottom: 0.25em;
      display: flex;
      justify-content: space-between;
      gap: 1em;
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
      border: 1px solid #ddd;
      display: block;
      margin: 0 auto;
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
      margin-bottom: 1.4em;
      font-size: 10.5pt;
      line-height: 1.5;
      text-align: justify;
    }}

    .footer {{
      margin-top: 2em;
      font-size: 10pt;
      text-align: center;
      color: #444;
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
      <li>Resumo executivo</li>
      <li>Objetivos</li>
      <li>Metodologia e evidência dos notebooks</li>
      <li>Diagnóstico exploratório</li>
      <li>Resultados de validação</li>
      <li>Avaliação final no teste reservado</li>
      <li>Conclusão final</li>
    </ol>
  </section>

  <h2 id="resumo-executivo">1. Resumo executivo</h2>
  <div class="resumo-box">
    <p>
      Este projeto avaliou a classificação binária da qualidade de vinhos com base em atributos físico-químicos.
      A regra adotada foi <strong>quality &ge; 7</strong> para a classe positiva e <strong>quality &lt; 7</strong>
      para a classe negativa. Como a classe relevante é minoritária, a acurácia isolada não é critério suficiente para a decisão.
    </p>
    <p>
      A recomendação principal do projeto é o <strong>Random Forest com balanceamento de classes</strong>.
      A decisão final foi orientada pelo conjunto de teste reservado e pela métrica de equilíbrio da classe positiva.
      O critério principal foi <strong>F1, recall, precision e ROC-AUC</strong>, e não apenas a acurácia bruta.
      O <strong>HistGradientBoosting</strong> permanece como alternativa forte quando a organização prioriza precision,
      mas o Random Forest mostrou melhor equilíbrio geral no conjunto final.
    </p>
  </div>

  <div class="kpis">
    <div class="kpi"><strong>0.6667</strong>F1 no HistGradientBoosting em validação</div>
    <div class="kpi"><strong>0.6563</strong>F1 do Random Forest em validação</div>
    <div class="kpi"><strong>0.6462</strong>F1 do Random Forest no teste final</div>
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
    A sequência analítica foi organizada para validar a definição da classe alvo, testar a separação entre treino e teste, comparar modelos e confirmar a decisão final com base em evidência. O problema é desbalanceado e exige atenção especial à classe positiva.
  </p>

  <h3>Evidência dos notebooks</h3>
  <p>
    A análise exploratória confirmou que a classe de alta qualidade é minoritária, com cerca de 13,9% dos casos. Isso torna F1, recall e ROC-AUC mais relevantes do que acurácia isolada. A variável álcool mostrou diferença clara entre classes, e a correlação entre atributos reforçou que a qualidade depende de combinações de sinais físico-químicos, não de um único preditor isolado.
  </p>

  <h3>Decisão metodológica</h3>
  <p>
    O conjunto de testes e diagnósticos mostrou que a regressão linear não é a solução principal, a divisão estratificada entre treino e teste foi adequada e a validação cruzada reforçou a estabilidade do modelo. A árvore de decisão foi útil para explicabilidade, mas não superou a melhor performance global dos modelos de ensemble.
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
  <p>
    O conjunto de gráficos reforça que a decisão final foi tomada a partir de evidência analítica e não por hipótese. Abaixo, cada figura acompanha a interpretação direta do que foi observado e a relevância para a escolha do modelo.
  </p>
  {notebook_sections_html}

  <h2 id="resultados-validacao">5. Resultados de validação</h2>
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

  <h2 id="avaliacao-teste">6. Avaliação final no teste reservado</h2>
  <figure>
    <img src="figures/final_model_comparison.png" alt="Comparação final no conjunto de teste" />
    <figcaption>Figura 5 — Comparação final no conjunto de teste.</figcaption>
  </figure>

  <p>
    O conjunto de teste reservado foi a etapa decisiva para a recomendação principal. O Random Forest balanceado manteve melhor equilíbrio entre detecção da classe positiva e estabilidade geral, enquanto o HistGradientBoosting continuou forte em precision. A diferença principal está no trade-off entre recall e precision: o Random Forest respondeu melhor ao problema em termos de equilíbrio geral e foi escolhido como modelo principal.
  </p>

  {build_table(test_rows, ['Modelo', 'Acurácia', 'Precision', 'Recall', 'F1', 'ROC-AUC', 'Average Precision'])}

  <p>
    Em termos práticos, o <strong>Random Forest</strong> mostrou melhor equilíbrio entre os indicadores relevantes para um problema desbalanceado. Já o <strong>HistGradientBoosting</strong> permaneceu como alternativa sólida quando a organização prioriza precisão e aceita uma queda no recall.
  </p>

  <h2 id="conclusao-final">7. Conclusão final</h2>
  <p>A recomendação final do projeto é:</p>
  <ul>
    <li><strong>Random Forest balanced</strong> como modelo principal para a solução de negócio;</li>
    <li><strong>HistGradientBoosting</strong> como alternativa preferencial quando a organização prioriza precision;</li>
    <li><strong>regressão linear</strong> e <strong>clusterização</strong> como diagnósticos e ferramentas complementares, mas não como solução principal;</li>
    <li><strong>árvore de decisão</strong> como apoio interpretativo, não como substituta da melhor performance global.</li>
  </ul>
  <p>
    Em síntese, a decisão foi guiada por evidência de validação e pelo conjunto de teste protegido, e não por suposição.
    O melhor equilíbrio entre identificação da classe positiva e robustez geral saiu para o Random Forest balanceado no teste final.
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
    html_path = REPORTS_DIR / 'relatorio_executivo.html'
    pdf_path = REPORTS_DIR / 'relatorio_executivo.pdf'

    html_path.write_text(html_content, encoding='utf-8')

    HTML(string=html_content, base_url=str(REPORTS_DIR)).write_pdf(str(pdf_path))
    print(f'HTML salvo em: {html_path}')
    print(f'PDF salvo em: {pdf_path}')


if __name__ == '__main__':
    main()
