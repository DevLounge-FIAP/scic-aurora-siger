# SCIC - Sistema de Comunicação Interplanetária da Colônia (Aurora Siger)

Protótipo desenvolvido para a Atividade Integradora da Fase 6 (FIAP). O sistema organiza dados
operacionais e de comunicação simulados da colônia Aurora Siger, avalia a confiabilidade de uma
previsão simples de latência, prioriza alertas críticos, permite consultas por prefixo e apoia a
decisão com uma análise final dos resultados.

## O que o sistema faz

- Carrega a base simulada (`dados_aurora_siger.csv`: 80 registros, 8 módulos, 10 ciclos).
- Prevê a latência de cada módulo a partir de tensão e corrente (regressão linear, scikit-learn).
- Avalia o modelo com **MAE, MSE, RMSE e R²** e gera gráficos de dispersão e de resíduos.
- Calcula **erro absoluto e erro relativo** entre latência observada e prevista, e classifica cada
  caso em uma severidade de 1 a 5.
- Demonstra **ponto flutuante** (IEEE 754) e **Método de Euler** (atenuação de sinal).
- Prioriza alertas com **heap** (`heapify-up` e `heapify-down`).
- Busca módulos e códigos de sensores por prefixo com **trie**.
- Relaciona os resultados com gerenciamento inteligente da comunicação (sensores, monitoramento,
  redundância, manutenção preditiva e microrrede).
- Converte IDs de sensores entre **hexadecimal, decimal e binário** e calcula **P = V x I** e
  **R = V / I** (Lei de Ohm).

## Arquivos da entrega

| Arquivo | Função |
|---|---|
| `codigo_fonte.py` | **Programa principal**: menu de terminal que une todos os módulos |
| `dados_aurora_siger.csv` | Base de dados simulada da colônia |
| `ml_model.py` | Modelo de previsão de latência, métricas e gráficos |
| `numerical_analysis.py` | Erros absoluto/relativo, Euler, ponto flutuante, severidade e alertas |
| `structures.py` | Classes `AlertHeap` (fila de prioridade) e `PrefixTrie` (busca por prefixo) |
| `hardware_coa.py` | Conversão de bases numéricas e cálculos elétricos |
| `gerar_dados.py` | Script que gera a base simulada (uso opcional) |
| `teste_*.py` | Testes de cada módulo (`teste_hardware`, `teste_ml`, `teste_numerical`, `teste_structures`) |
| `requirements.txt` | Dependências do projeto |
| `relatorio_tecnico.md` | Relatório técnico completo |
| `link_video.txt` | Link do vídeo de apresentação (YouTube, não listado) |
| `graficos_ou_imagens/` | Gráficos gerados pelo modelo (dispersão, resíduos e painel de performance) |

## Dependências

Python 3.10 ou superior. Bibliotecas (todas permitidas na fase, nenhuma adicional):

| Biblioteca | Uso no projeto |
|---|---|
| pandas | leitura, organização e análise dos dados |
| numpy | cálculos numéricos |
| scikit-learn | regressão linear, divisão treino/teste e métricas |
| matplotlib e seaborn | gráficos de performance |

Instalação:

```bash
pip install -r requirements.txt
```

## Como executar

Na pasta do projeto:

```bash
python codigo_fonte.py
```

O menu aparece no terminal. Digite o número da opção e pressione Enter. Ao final de cada opção,
pressione Enter para voltar ao menu.

> **Atenção:** as opções que carregam a base (a 1, ou qualquer outra se a base ainda não foi
> carregada) **atualizam o arquivo `dados_aurora_siger.csv`** com as colunas calculadas (previsão,
> erros e severidade). Isso é esperado. Se quiser recomeçar do zero, execute
> `python gerar_dados.py` e depois use o menu normalmente.

## Como usar o menu

Comece pela opção 1. Se você pular essa etapa, o programa carrega a base sozinho.

| Opção | O que faz | O que digitar |
|---|---|---|
| 1 | Carrega o CSV, treina o modelo, calcula erros e gera os alertas | nada |
| 2 | Consulta registros | `1` + começo do nome do módulo (ex.: `hab`), ou `2` + ciclo (1 a 10), ou `3` + status (`ativo`, `alerta`, `manutencao`) |
| 3 | Indicadores por módulo, erros, ponto flutuante e Euler | nada |
| 4 | Previsão de latência | tensão (V) e corrente (A). Aceita vírgula ou ponto |
| 5 | Métricas do modelo (MAE, MSE, RMSE, R²) e caminho dos gráficos | nada |
| 6 | Os 5 alertas mais urgentes, via heap | nada |
| 7 | Busca por prefixo (trie) | começo de um módulo ou código (ex.: `lab` ou `0xC`) |
| 8 | Dispositivos de entrada/saída, bases numéricas e eletricidade | nada |
| 9 | Análise final dos resultados | nada |
| 10 | Gerenciamento inteligente da comunicação, calculado com os dados | nada |
| 0 | Sair | nada |

## Exemplos de execução

**Opção 4 - previsão** (tensão 12,5 V e corrente 3,0 A):

```
Faixa observada na colônia: tensão 4.7 a 25.3 V | corrente 1.2 a 8.8 A
Latência prevista: 53.66 ms  (P = 37.50 W)
```

Se os valores saírem da faixa da colônia, o programa calcula e avisa que o modelo está
extrapolando. Por exemplo, 500 V e 3 A geram uma previsão sem sentido físico (cerca de 1397 ms),
o que mostra que a regressão linear só é confiável dentro da faixa em que foi treinada.

**Opção 5 - métricas** (conjunto de teste):

```
MAE, MSE, RMSE e R² calculados; R² = 0.6749 | RMSE = 3.5827 ms
```

**Opção 6 - alerta mais urgente:**

```
1. Modulo: Habitat | Sensor: 0xD404 | Severidade: 5 | Prioridade: 4 | Erro: 7.46 ms
   Habitat: latência 7.5 ms acima do previsto (12.1% de erro, status: alerta)
```

**Opção 7 - busca por prefixo `0xC`:**

```
0xC302  (Comunicacao) -> decimal 49922 | binário 1100001100000010
```

**Opção 9 - análise final** (trecho):

```
Módulo com maior erro relativo médio: Laboratorio
  Habitat: latência real fica em média 6.7 ms acima do previsto
  Laboratorio: latência real fica em média 5.1 ms abaixo do previsto
```

## Critério de prioridade dos alertas

O heap ordena os alertas por: (1) maior severidade; (2) em caso de empate, módulo mais essencial
(prioridade 1 vence); (3) em novo empate, maior erro absoluto. A severidade (1 a 5) vem do erro
relativo (abaixo de 5% = 1, até 10% = 2, até 20% = 3, até 35% = 4, acima = 5) somado a um bônus
pelo status do módulo (`manutencao` +1, `alerta` +2), limitado a 5.

## Testes

Cada módulo possui um arquivo de testes com `assert`:

```bash
python teste_hardware.py
python teste_numerical.py
python teste_ml.py
python teste_structures.py
```

O `teste_structures.py` termina com duas demonstrações interativas (autocomplete e busca exata):
digite `sair` para encerrá-las. Os testes de ML e de análise numérica trabalham com o CSV da pasta.

## Limitações conhecidas

- O modelo usa só tensão e corrente e não sabe qual é o módulo. Por isso erra sempre para o mesmo
  lado em alguns módulos (Habitat para menos, Laboratório para mais).
- A previsão é aplicada a todos os 80 registros, inclusive aos usados no treino, então os erros
  dessas linhas são mais otimistas do que seriam em dados novos.
- Os dados são simulados e os sensores, redes e interfaces (USB, Wi-Fi, Bluetooth) são apenas
  conceituais.

## Equipe

- Bruno (dados, hardware e vídeo de apresentação);
- Aelton (aprendizado de máquina);
- Michelly (estruturas de dados);
- Victor (análise numérica, integração e documentação).