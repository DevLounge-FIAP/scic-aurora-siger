# Projeto Aurora Fase 6 - Divisão de Responsabilidades

Para que o desenvolvimento ocorra sem gargalos em 4 semanas e sem duplicidade de dados mockados, os membros técnicos trabalham em uma esteira sequencial onde a saída de uma semana alimenta diretamente a entrada da seguinte, enquanto o quinto membro orquestra a documentação, os capítulos teóricos e a entrega final.

## Divisão de Responsabilidades por Membro

### Membro 1 - Engenharia de Dados, Hardware e Elétrica Básica (Semana 1)(Bruno)

**Escopo técnico:** Criar a base de dados oficial da missão (`dados_aurora_siger.csv`) contendo registros de módulos, tipos, IDs de sensores, grandezas elétricas e latências observadas. Implementar o módulo de Arquitetura de Computadores (`hardware_coa.py`): funções de conversão de bases numéricas (Hexadecimal, Binário e Decimal a partir dos IDs dos sensores) e rotinas de cálculo elétrico via Lei de Ohm ($P = V \times I$ e $R = V / I$) para estimar potência e resistência de transmissão dos módulos.

**Entregável da semana:** Arquivo `dados_aurora_siger.csv` gerado com telemetria inicial e módulo `hardware_coa.py` testado com funções desacopladas de conversão e cálculo de potência.

**Passagem para a próxima semana:** O Membro 2 consumirá diretamente o `dados_aurora_siger.csv` gerado para utilizar as variáveis elétricas e operacionais como features preditivas.



### Membro 2 - Aprendizado de Máquina e Regressão Linear (Semana 2) (Aelton)

**Escopo técnico:** Carregar a base gerada na Semana 1 e desenvolver o pipeline de regressão com Scikit-Learn no módulo `ml_model.py` para estimar a latência dos módulos. Realizar a divisão formal entre treino e teste e calcular obrigatoriamente as quatro métricas: MAE, MSE, RMSE e $R^2$. Gerar gráficos comparativos (valores reais vs. previstos e análise de resíduos) via Matplotlib/Seaborn exportados para a pasta `graficos_ou_imagens/`. Executar a inferência em todo o dataset e adicionar a coluna calculada `latencia_prevista_ms`.

**Entregável da semana:** Módulo `ml_model.py` pronto, gráficos de dispersão exportados e arquivo `dados_aurora_siger.csv` atualizado com a coluna `latencia_prevista_ms`.

**Passagem para a próxima semana:** O Membro 3 consumirá o CSV enriquecido com latência real e prevista para a realização das análises de erro numérico.



### Membro 3 - Métodos Numéricos e Análise de Erros (Semana 3) (Maria)

**Escopo técnico:** Consumir o dataset atualizado pelo Membro 2 e desenvolver o módulo `numerical_analysis.py` contendo funções para calcular o Erro Absoluto ($\vert{}y - \hat{y}\vert{}$) e o Erro Relativo ($\frac{\vert{}y - \hat{y}\vert{}}{y}$) módulo a módulo. Desenvolver simulação temporal iterativa via Método de Euler para modelar a atenuação de sinal ao longo do tempo e tratar limitações de ponto flutuante (IEEE 754). Estabelecer regra para cálculo de criticidade (escala de 1 a 5) com base no erro e no status, gerando a lista estruturada de alertas operacionais.

**Entregável da semana:** Módulo `numerical_analysis.py` validado e lista de dicionários contendo os alertas operacionais pontuados por nível de severidade.

**Passagem para a próxima semana:** O Membro 4 consumirá a lista de alertas com criticidade calculada para alimentar o Heap, além dos nomes de módulos e IDs para indexação na Trie.



### Membro 4 - Algoritmos e Estruturas de Dados Avançadas (Semana 4) (Michelly)

**Escopo técnico:** Implementar no módulo `structures.py` a classe `AlertHeap` (fila de prioridade com rotinas explícitas de `heapify-up` e `heapify-down`) consumindo os alertas da Semana 3 para ordenar e extrair os eventos mais críticos em $O(\log N)$. Implementar a estrutura `PrefixTrie` (árvore de prefixos) com métodos de inserção, busca exata e autocomplete para indexação rápida de nomes de módulos e códigos hexadecimais de sensores da colônia.

**Entregável da semana:** Módulo `structures.py` completo contendo as classes `AlertHeap` e `PrefixTrie` com testes unitários comprovando inserção, priorização e consultas por prefixo.

**Passagem para a finalização:** O Membro 5 consumirá as classes de `structures.py` para conectar a priorização de alertas e buscas aos menus do terminal CLI.



### Membro 5 - Líder Técnico, Documentador e Integrador (Contínuo) (Victor)

**Escopo técnico:** Redigir as seções conceituais do trabalho: Gerenciamento Inteligente de Comunicação (IoT, microrredes, telemetria SCADA, redundância de enlace e manutenção preditiva) e a Reflexão Social, Cultural e Sustentável (cultura afro-brasileira/indígena na gestão de recursos, governança de IA e supervisão humana contra vieses). Montar a interface principal (`codigo_fonte.py` com menu interativo CLI unificando os módulos de 1 a 4). Consolidar `relatorio_tecnico.md/.pdf`, `README.md`, produzir/gravar o vídeo demonstrativo de 5 minutos no YouTube (não listado), preencher `link_video.txt` e empacotar o arquivo `.zip` final.

**Entregável final:** Pacote `.zip` completo contendo o executável CLI unificado, a base de dados, relatórios técnicos, README e link do vídeo.



## Cronograma Semanal de Execução (4 Semanas)

| Semana | Foco de Desenvolvimento | Insumo Consumido | Ação do Membro 5 (Integrador/Doc) |
| --- | --- | --- | --- |
| **Semana 1** | **Membro 1:** Gera base simulada inicial, cálculos da Lei de Ohm ($P = V \times I$) e conversor de bases hex/bin/dec. | Requisitos do SCIC e dicionário de dados da colônia. | Define schema das colunas do CSV, cria o repositório Git e redige a introdução/objetivos no `relatorio_tecnico.md`. |
| **Semana 2** | **Membro 2:** Treina regressão com Scikit-Learn, avalia métricas ($R^2$, MAE, MSE, RMSE) e gera gráficos. | `dados_aurora_siger.csv` com dados brutos gerados na Semana 1. | Redige o capítulo de Gerenciamento Inteligente da Comunicação (Seção 5.7) e valida o módulo `ml_model.py`. |
| **Semana 3** | **Membro 3:** Implementa erros absoluto/relativo, simulação por Euler e regra de severidade de alertas. | `dados_aurora_siger.csv` atualizado com a coluna `latencia_prevista_ms`. | Redige o capítulo de Reflexão Social, Cultural e Sustentável (Seção 5.8) e valida o módulo `numerical_analysis.py`. |
| **Semana 4** | **Membro 4:** Finaliza implementação e validação das classes `AlertHeap` e `PrefixTrie`. | Lista de alertas priorizados e nomes/sensores da Semana 3. | Unifica todos os scripts em `codigo_fonte.py` via CLI, grava o vídeo de 5 min, gera o relatório final e zipa o projeto. |

## Contrato de Independência Técnica

Para garantir a continuidade fluida da esteira sem retrabalho entre os membros:

### Contrato de Dados Evolutivo (Dataset Pipeline)
O arquivo `dados_aurora_siger.csv` evolui ao longo das semanas de forma incremental:

- **Gerado na Semana 1 (Membro 1):** `modulo_nome` (str), `modulo_tipo` (str), `sensor_hex_id` (str), `tensao_v` (float), `corrente_a` (float), `latencia_observada_ms` (float), `status` (str).
- **Acrescido na Semana 2 (Membro 2):** `latencia_prevista_ms` (float).
- **Processado na Semana 3 (Membro 3):** `erro_absoluto` (float), `erro_relativo` (float) e `severidade_alerta` (int de 1 a 5).



### Isolamento e Reutilização dos Módulos

Cada integrante desenvolve seu script contendo funções bem definidas (ex.: `converter_base()`, `treinar_modelo()`, `calcular_erros()`, `inserir_heap()`) acompanhado de um bloco `if __name__ == "__main__":` com testes rápidos, garantindo que o código rode de forma independente antes de ser repassado ao próximo integrante.

### Empacotamento Centralizado

Ao final da Semana 4, o Membro 5 importa os arquivos prontos (`from hardware_coa import ...`, `from ml_model import ...`, `from numerical_analysis import ...`, `from structures import ...`) dentro do script central `codigo_fonte.py`, expondo todas as funcionalidades em um menu iterativo no terminal sem alterar a lógica interna desenvolvida pelos demais.