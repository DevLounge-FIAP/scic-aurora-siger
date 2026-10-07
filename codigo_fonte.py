"""
codigo_fonte.py - SCIC / Aurora Siger (Fase 6)
Sistema de Comunicação Interplanetária da Colônia - PROGRAMA PRINCIPAL

Este arquivo é o "maestro": ele não refaz nenhum cálculo, só chama os módulos da equipe
e mostra os resultados em um menu de terminal.

    ml_model.py            -> modelo de previsão de latência + métricas (MAE, MSE, RMSE, R²)
    numerical_analysis.py  -> erro absoluto/relativo, ponto flutuante, Euler, alertas
    structures.py          -> AlertHeap (fila de prioridade) e PrefixTrie (busca por prefixo)
    hardware_coa.py        -> bases numéricas (hex/dec/bin) e eletricidade (P = V x I)

Como executar:  python codigo_fonte.py
"""

import pandas as pd

import hardware_coa
import ml_model
import numerical_analysis as na
from structures import AlertHeap, PrefixTrie

# ---------------------------------------------------------------------------
# Estado do programa: guarda o que já foi carregado para não recalcular a cada opção
# ---------------------------------------------------------------------------
estado = {"df": None, "alertas": None, "resultado_ml": None}

COLUNAS_CONSULTA = [
    "modulo_nome", "sensor_hex_id", "ciclo", "status",
    "latencia_observada_ms", "latencia_prevista_ms", "erro_absoluto", "erro_relativo",
]
LIMITE_LINHAS = 20  # evita encher a tela em consultas grandes


def titulo(texto):
    """Imprime um cabeçalho padronizado."""
    print("\n" + "=" * 62)
    print(f"  {texto}")
    print("=" * 62)


# ---------------------------------------------------------------------------
# 1. Carregar dados (e rodar a cadeia: previsão -> erros -> alertas)
# ---------------------------------------------------------------------------
def carregar_base():
    """Ordem importa: o ML cria a coluna 'latencia_prevista_ms', e só depois
    a análise numérica consegue calcular erros e severidade."""
    titulo("1 - CARREGAR DADOS DA COLÔNIA")
    estado["resultado_ml"] = ml_model.executar_pipeline_completo(exibir_detalhes=False)
    df, alertas = na.processar_dataset()
    estado["df"], estado["alertas"] = df, alertas

    print(f"✓ {len(df)} registros carregados de 'dados_aurora_siger.csv'")
    print(f"✓ Módulos: {df['modulo_nome'].nunique()} | Ciclos: {df['ciclo'].nunique()}")
    print("✓ Previsão de latência calculada pelo modelo de regressão linear")
    print(f"✓ Erros calculados e {len(alertas)} alertas gerados (severidade >= 3)")


def garantir_base():
    """Se o usuário pular a opção 1, carrega sozinho."""
    if estado["df"] is None:
        print("(Base ainda não carregada, carregando agora...)")
        carregar_base()
    return estado["df"]


# ---------------------------------------------------------------------------
# 2. Consultar registros
# ---------------------------------------------------------------------------
def mostrar_tabela(tabela):
    if tabela.empty:
        print("Nenhum registro encontrado.")
        return
    print(tabela[COLUNAS_CONSULTA].head(LIMITE_LINHAS).to_string(index=False))
    if len(tabela) > LIMITE_LINHAS:
        print(f"... mostrando {LIMITE_LINHAS} de {len(tabela)} registros.")


def consultar_registros():
    df = garantir_base()
    titulo("2 - CONSULTAR REGISTROS")
    print("1 - Por módulo (digite o começo do nome, ex.: 'hab')")
    print("2 - Por ciclo (1 a 10)")
    print("3 - Por status (ativo, alerta, manutencao)")
    escolha = input("Escolha: ").strip()

    if escolha == "1":
        prefixo = input("Prefixo do módulo: ").strip()
        trie = PrefixTrie()
        trie.inserir_df(df, colunas=("modulo_nome",))  # trie só com nomes de módulos
        nomes = [n.lower() for n in trie.autocomplete(prefixo)]
        mostrar_tabela(df[df["modulo_nome"].str.lower().isin(nomes)])
    elif escolha == "2":
        texto = input("Ciclo: ").strip()
        if texto.isdigit():
            mostrar_tabela(df[df["ciclo"] == int(texto)])
        else:
            print("Digite um número inteiro.")
    elif escolha == "3":
        status = input("Status: ").strip().lower()
        mostrar_tabela(df[df["status"].str.lower() == status])
    else:
        print("Opção inválida.")


# ---------------------------------------------------------------------------
# 3. Indicadores e erros numéricos
# ---------------------------------------------------------------------------
def mostrar_indicadores():
    df = garantir_base()
    titulo("3 - INDICADORES E ERROS NUMÉRICOS")

    d = df.copy()
    d["potencia_w"] = d["tensao_v"] * d["corrente_a"]  # P = V x I
    resumo = d.groupby("modulo_nome").agg(
        latencia_media_ms=("latencia_observada_ms", "mean"),
        erro_abs_medio_ms=("erro_absoluto", "mean"),
        erro_rel_medio=("erro_relativo", "mean"),
        potencia_media_w=("potencia_w", "mean"),
    )
    resumo["erro_rel_medio"] = resumo["erro_rel_medio"] * 100  # fração -> %
    print(resumo.round(2).rename(columns={"erro_rel_medio": "erro_rel_medio_%"}).to_string())

    print("\nComo interpretar o erro relativo (regra usada no projeto):")
    print("  < 5%   : aceitável (previsão confiável)")
    print("  5-20%  : atenção (monitorar o módulo)")
    print("  > 20%  : preocupante (pode virar alerta crítico na colônia)")

    print("\nPonto flutuante (por que usamos arredondamento e isclose):")
    pf = na.demonstrar_ponto_flutuante()
    print(f"  0.1 + 0.2 = {pf['soma_com_17_casas']}  (== 0.3? {pf['igualdade_direta']})")
    print(f"  Com tolerância (math.isclose): {pf['igualdade_com_tolerancia']}")

    print("\nSimulação de atenuação de sinal (Método de Euler, 5 primeiros passos):")
    for p in na.simular_atenuacao_euler()[:5]:
        print(f"  t={p['tempo']:.1f}s | Euler={p['sinal_euler']:.2f} | "
              f"exato={p['sinal_exato']:.2f} | erro={p['erro_absoluto']:.2f}")


# ---------------------------------------------------------------------------
# 4. Previsão simples
# ---------------------------------------------------------------------------
def prever_latencia():
    df = garantir_base()
    titulo("4 - PREVISÃO DE LATÊNCIA")
    modelo = estado["resultado_ml"]["modelo"]

    # Faixa observada na colônia: serve de guia para o usuário digitar valores realistas
    v_min, v_max = df["tensao_v"].min(), df["tensao_v"].max()
    i_min, i_max = df["corrente_a"].min(), df["corrente_a"].max()
    print(f"Faixa observada na colônia: tensão {v_min:.1f} a {v_max:.1f} V | "
          f"corrente {i_min:.1f} a {i_max:.1f} A")
    try:
        tensao = float(input("Tensão do módulo (V): ").replace(",", "."))
        corrente = float(input("Corrente do módulo (A): ").replace(",", "."))
    except ValueError:
        print("Valor inválido. Use números, ex.: 12.5")
        return
    if tensao <= 0 or corrente <= 0:
        print("Tensão e corrente precisam ser maiores que zero.")
        return

    entrada = pd.DataFrame([[tensao, corrente]], columns=ml_model.FEATURES_PADRAO)
    previsao = modelo.predict(entrada)[0]
    print(f"\nLatência prevista: {previsao:.2f} ms  (P = {tensao * corrente:.2f} W)")
    if not (v_min <= tensao <= v_max and i_min <= corrente <= i_max):
        print("ATENÇÃO: valores fora da faixa observada. O modelo está extrapolando,")
        print("então confie menos nesta previsão.")
    print("Obs.: o modelo usa só tensão e corrente, então é uma estimativa simples.")


# ---------------------------------------------------------------------------
# 5. Métricas de performance
# ---------------------------------------------------------------------------
def mostrar_metricas():
    garantir_base()
    titulo("5 - AVALIAÇÃO DO MODELO (MAE, MSE, RMSE, R²)")
    r = estado["resultado_ml"]
    print(ml_model.interpretar_metricas(r["metricas_teste"], "Conjunto de Teste", r["metricas_baseline"]))
    print(ml_model.formatar_comparacao_modelos(r["comparacao_modelos"]))
    m = r["metricas_completo"]
    print(f"Base completa: MAE={m['MAE']} ms | RMSE={m['RMSE']} ms | R²={m['R2']}")
    print("\nGráficos salvos em:")
    for caminho in r["graficos"]:
        print(f"  -> {caminho}")


# ---------------------------------------------------------------------------
# 6. Priorização de alertas com heap
# ---------------------------------------------------------------------------
def priorizar_alertas():
    garantir_base()
    titulo("6 - PRIORIZAÇÃO DE ALERTAS (HEAP)")
    alertas = estado["alertas"]
    if not alertas:
        print("Nenhum alerta crítico no momento.")
        return

    heap = AlertHeap()
    for alerta in alertas:
        heap.inserir(alerta)  # cada inserção usa heapify-up
    print(f"{len(alertas)} alertas inseridos no heap.")
    print("Critério: maior severidade; empate -> módulo mais essencial (prioridade 1);")
    print("          novo empate -> maior erro absoluto.\n")

    print("Os 5 alertas mais urgentes (cada remoção usa heapify-down):")
    for posicao in range(1, 6):
        alerta = heap.remover_alerta_prioritario()
        if alerta is None:
            break
        print(f"{posicao}. {heap.formatar(alerta)}")
        print(f"   {alerta['mensagem']}")

    print("\nVantagem sobre lista simples: achar o mais urgente é O(1) e remover/inserir")
    print("custa O(log N); uma lista exigiria reordenar tudo (O(N log N)) a cada novo alerta.")


# ---------------------------------------------------------------------------
# 7. Busca por prefixo com trie
# ---------------------------------------------------------------------------
def buscar_prefixo():
    df = garantir_base()
    titulo("7 - BUSCA POR PREFIXO (TRIE)")
    trie = PrefixTrie()
    trie.inserir_df(df)  # indexa nomes de módulos e códigos hex dos sensores
    prefixo = input("Digite o prefixo (ex.: 'lab' ou '0xC'): ").strip()
    resultados = trie.autocomplete(prefixo)

    if not resultados:
        print("Nenhum módulo ou sensor começa com esse prefixo.")
        return
    print(f"\n{len(resultados)} resultado(s):")
    for item in resultados[:LIMITE_LINHAS]:
        if item.lower().startswith("0x"):
            modulo = df.loc[df["sensor_hex_id"] == item, "modulo_nome"].iloc[0]
            c = hardware_coa.converter_id(item)
            print(f"  {item}  ({modulo}) -> decimal {c['decimal']} | binário {c['binario']}")
        else:
            print(f"  {item}  (módulo)")
    if len(resultados) > LIMITE_LINHAS:
        print(f"  ... e mais {len(resultados) - LIMITE_LINHAS}.")


# ---------------------------------------------------------------------------
# 8. Dispositivos, bases numéricas e eletricidade
# ---------------------------------------------------------------------------
def mostrar_hardware():
    df = garantir_base()
    titulo("8 - DISPOSITIVOS, BASES NUMÉRICAS E ELETRICIDADE")
    print("Entrada de dados: sensores/medidores simulados (arquivo CSV).")
    print("Saída de dados:   terminal, gráficos (PNG) e relatório.")
    print("Interfaces (conceitual): rede, Wi-Fi, USB, Bluetooth.\n")

    for _, linha in df.drop_duplicates("modulo_nome").iterrows():
        c = hardware_coa.converter_id(linha["sensor_hex_id"])
        e = hardware_coa.calcular_eletrico(linha["modulo_nome"], linha["tensao_v"], linha["corrente_a"])
        print(f"{linha['modulo_nome']:<17} {c['hex']:<7} dec={c['decimal']:<6} bin={c['binario']:<16} "
              f"P={e['potencia_w']:.2f} W  R={e['resistencia_ohm']:.2f} Ω")
    print("\nFórmulas: P = V x I (potência) | R = V / I (Lei de Ohm)")


# ---------------------------------------------------------------------------
# 9. Análise final
# ---------------------------------------------------------------------------
def analise_final():
    df = garantir_base()
    alertas = estado["alertas"]
    r = estado["resultado_ml"]
    titulo("9 - ANÁLISE FINAL DOS RESULTADOS")

    print(f"Registros analisados: {len(df)} | Módulos: {df['modulo_nome'].nunique()}")
    print("Status operacional:", df["status"].value_counts().to_dict())
    pior = df.groupby("modulo_nome")["erro_relativo"].mean().idxmax()
    print(f"Módulo com maior erro relativo médio: {pior}")
    # Erro COM SINAL médio: mostra se o modelo erra sempre para o mesmo lado (viés)
    vies = df.groupby("modulo_nome")["diferenca_ms"].mean()
    for nome in vies.abs().sort_values(ascending=False).index[:2]:
        sentido = "acima" if vies[nome] > 0 else "abaixo"
        print(f"  {nome}: latência real fica em média {abs(vies[nome]):.1f} ms {sentido} do previsto")
    print(f"Modelo: R² = {r['metricas_teste']['R2']} | RMSE = {r['metricas_teste']['RMSE']} ms (teste)")
    print(f"Alertas críticos: {len(alertas)} | Acima do previsto: "
          f"{len(na.filtrar_acima_do_previsto(alertas))}")
    if alertas:
        print(f"Mais urgente: {alertas[0]['mensagem']}")

    print("\nConclusão: erros grandes e repetidos em um mesmo módulo indicam um problema")
    print("do modelo (que só enxerga tensão e corrente) ou do enlace, e não só ruído.")
    print("Os alertas são apoio à decisão: a equipe humana valida antes de agir.")


# ---------------------------------------------------------------------------
# 10. Gerenciamento inteligente da comunicação
# ---------------------------------------------------------------------------
def gerenciamento_inteligente():
    """Liga os resultados do SCIC aos conceitos de gestão inteligente da comunicação."""
    df = garantir_base()
    alertas = estado["alertas"]
    titulo("10 - GERENCIAMENTO INTELIGENTE DA COMUNICAÇÃO")

    # Sensores e monitoramento contínuo
    print(f"Sensores: {df['sensor_hex_id'].nunique()} códigos distintos monitorando "
          f"{df['modulo_nome'].nunique()} módulos em {df['ciclo'].nunique()} ciclos.")
    desvios = int((df["erro_relativo"] >= 0.05).sum())
    print(f"Monitoramento: {desvios} de {len(df)} registros têm erro relativo >= 5% "
          f"({len(alertas)} viraram alertas).")
    contagem = pd.Series([a["modulo_nome"] for a in alertas]).value_counts()
    if not contagem.empty:
        print("  Alertas por módulo (desvio que se repete = sinal mais forte):")
        for nome, qtd in contagem.items():
            total = int((df["modulo_nome"] == nome).sum())
            print(f"    {nome}: {qtd} de {total} registros")

    # Automação
    if alertas:
        heap = AlertHeap()
        for alerta in alertas:
            heap.inserir(alerta)
        print(f"\nAutomação: o heap entrega o alerta mais urgente sem busca manual -> "
              f"{heap.alerta_prioritario()['modulo_nome']} "
              f"(sensor {heap.alerta_prioritario()['sensor_hex_id']}).")

    # Redundância de enlaces
    comunicacao = df[df["modulo_tipo"] == "comunicacao"]
    print("\nRedundância (módulos de comunicação, um poderia ser enlace reserva do outro):")
    for nome, grupo in comunicacao.groupby("modulo_nome"):
        print(f"    {nome}: latência média {grupo['latencia_observada_ms'].mean():.1f} ms | "
              f"erro relativo médio {grupo['erro_relativo'].mean() * 100:.1f}%")

    # Manutenção preditiva
    em_manutencao = df[df["status"].str.lower() == "manutencao"]
    print(f"\nManutenção preditiva: {len(em_manutencao)} registros em manutenção. "
          "Desvios repetidos no mesmo sentido indicam o módulo a inspecionar antes da falha:")
    vies = df.groupby("modulo_nome")["diferenca_ms"].mean()
    for nome in vies.abs().sort_values(ascending=False).index[:2]:
        sentido = "acima" if vies[nome] > 0 else "abaixo"
        print(f"    {nome}: em média {abs(vies[nome]):.1f} ms {sentido} do previsto")

    # Microrrede
    potencia = (df["tensao_v"] * df["corrente_a"]).groupby(df["modulo_nome"]).mean()
    print(f"\nMicrorrede: potência média somada dos módulos = {potencia.sum():.0f} W; "
          f"maior consumo: {potencia.idxmax()} ({potencia.max():.0f} W).")
    print("\nO sistema apoia a decisão; a equipe humana valida antes de agir.")


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------
OPCOES = {
    "1": ("Carregar dados da colônia", "lê o CSV, treina o modelo, calcula erros e gera os alertas", carregar_base),
    "2": ("Consultar registros", "filtra por módulo, ciclo ou status", consultar_registros),
    "3": ("Calcular indicadores e erros numéricos", "erro absoluto/relativo, ponto flutuante e Euler", mostrar_indicadores),
    "4": ("Executar previsão de latência", "você digita tensão e corrente, o modelo estima a latência", prever_latencia),
    "5": ("Avaliar desempenho do modelo", "MAE, MSE, RMSE e R² com interpretação", mostrar_metricas),
    "6": ("Priorizar alertas (heap)", "mostra os 5 alertas mais urgentes da fila de prioridade", priorizar_alertas),
    "7": ("Buscar por prefixo (trie)", "digite o começo de um módulo ou código de sensor", buscar_prefixo),
    "8": ("Dispositivos, bases e eletricidade", "hex/decimal/binário dos sensores e P = V x I", mostrar_hardware),
    "9": ("Exibir análise final", "resumo dos resultados e conclusão", analise_final),
    "10": ("Gerenciamento inteligente da comunicação", "sensores, redundância, manutenção preditiva e microrrede", gerenciamento_inteligente),
}


def menu():
    while True:
        titulo("SCIC - SISTEMA DE COMUNICAÇÃO INTERPLANETÁRIA - AURORA SIGER")
        print("  Dica: comece pela opção 1. Se pular, a base é carregada sozinha.\n")
        for chave, (nome, descricao, _) in OPCOES.items():
            print(f"  {chave} - {nome}")
            print(f"      {descricao}")
        print("  0 - Sair")
        try:
            opcao = input("\nEscolha uma opção: ").strip()
        except EOFError:  # entrada encerrada (ex.: execução automática)
            break
        if opcao == "0":
            print("Encerrando o SCIC. Missão Aurora Siger operando normalmente.")
            break
        if opcao in OPCOES:
            OPCOES[opcao][2]()
            try:
                input("\nPressione Enter para voltar ao menu...")
            except EOFError:
                break
        else:
            print("Opção inválida. Digite um número de 0 a 10.")


if __name__ == "__main__":
    menu()