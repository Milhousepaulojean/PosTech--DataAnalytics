# Resumo do preprocessamento

## Definição da variável alvo

O projeto é um problema de classificação binária para qualidade de vinho. O texto do desafio sugere a classe de alta qualidade como `quality >= 7`, enquanto `quality < 7` representa a classe baixa ou média.

Status: decisão provisória pendente de confirmação.

## Estratégia de split e justificativa

O split segue o charter do projeto e o fluxo seguro contra leakage:

1. dividir os dados completos em treino/validação e teste final antes de qualquer preprocessamento;
2. reservar o conjunto de teste final apenas para a avaliação final;
3. criar o split de treino/validação sobre a população restante antes de ajustar transformações;
4. usar estratificação para preservar as proporções da classe na presença de desbalanceamento.

Estratégia utilizada:
- conjunto de teste final: 20%
- split treino/validação: 25% de validação sobre os dados restantes
- `random_state`: 42
- estratificação: sim

Isso resulta em aproximadamente:
- treino: 60%
- validação: 20%
- teste: 20%

## Etapas de preprocessamento e origem do ajuste

O fluxo de preprocessamento foi mantido intencionalmente simples e restrito à etapa de preparação:

- remover a coluna identificadora `Id`;
- definir a variável alvo binária pela regra provisória `quality >= 7`;
- ajustar `StandardScaler` apenas sobre os dados de treino;
- aplicar o scaler ajustado aos dados de validação e teste sem refazer o ajuste.

O scaler ajustado é armazenado no objeto do pipeline usado pelo script de preparação e não é reutilizado para seleção de modelo fora do fluxo de treino/validação.

## Features excluídas ou transformadas

Features excluídas:
- `Id` foi removida das variáveis preditoras porque é um identificador e não representa um sinal válido para aprendizado.

Features transformadas:
- todas as colunas numéricas foram padronizadas com `StandardScaler`;
- `quality` foi convertida em variável alvo binária e removida do conjunto de preditores.

## Limitações e riscos conhecidos

- o threshold `quality >= 7` é um candidato forte, mas permanece pendente de confirmação;
- a classe positiva é substancialmente menor que a negativa, o que reforça a importância de métricas sensíveis à classe;
- várias variáveis apresentam possíveis outliers por IQR; esses valores devem ser revisados antes de inferências adicionais ou decisões finais de transformação;
- os datasets preparados existem para a próxima etapa de modelagem, mas nenhum modelo é treinado nesta etapa.

## Handoff para modelagem e validação

Os artefatos preparados estão prontos para passar para o especialista em modelagem e o revisor de validação:
- `data/prepared/train_prepared.csv`
- `data/prepared/validation_prepared.csv`
- `data/prepared/test_prepared.csv`

O conjunto de teste final permanece intocado para a etapa final de avaliação, e a escolha do modelo deve continuar sendo reportada com evidência de validação antes de o conjunto reservado ser usado para a aprovação final.
