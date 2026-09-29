"""
numerical_analysis.py - SCIC / Aurora Siger (Semana 3)

Responsabilidades deste módulo:
  1. Calcular erro absoluto e erro relativo (latência observada x prevista)
  2. Simular a atenuação de sinal com o Método de Euler
  3. Mostrar as limitações de ponto flutuante (IEEE 754)
  4. Calcular a severidade do alerta (escala de 1 a 5)
  5. Gerar a lista de alertas (list[dict]) que será usada pelo AlertHeap (Michelly)
"""

import math
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes (regras de negócio ficam aqui em cima para facilitar ajustes)
# ---------------------------------------------------------------------------
# Caminho do CSV ancorado na pasta deste arquivo: funciona de qualquer pasta.
CAMINHO_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_aurora_siger.csv")

COLUNA_REAL = "latencia_observada_ms"
COLUNA_PREVISTA = "latencia_prevista_ms"

# Faixas do erro relativo (fração: 0.05 = 5%) -> severidade base
# Ex.: erro < 5% => 1 | < 10% => 2 | < 20% => 3 | < 35% => 4 | resto => 5
FAIXAS_ERRO_RELATIVO = [(0.05, 1), (0.10, 2), (0.20, 3), (0.35, 4)]

# Bônus somados à severidade base conforme o status do módulo
BONUS_STATUS = {"ativo": 0, "manutencao": 1, "alerta": 2}

# Prioridade usada no desempate quando a coluna não existir no CSV (1 = mais essencial)
PRIORIDADE_PADRAO = 99


# ---------------------------------------------------------------------------
# 1. Erros numéricos
# ---------------------------------------------------------------------------
def calcular_erro_absoluto(real, previsto):
    """Erro absoluto = |y - y_previsto|. Diz QUANTO errou, na unidade original (ms)."""
    return abs(real - previsto)


def calcular_erro_relativo(real, previsto):
    """Erro relativo = |y - y_previsto| / y. Diz o quanto errou PROPORCIONALMENTE.

    Se o valor real for 0 não dá para dividir, então devolvemos None.
    """
    if real == 0:
        return None
    return abs(real - previsto) / abs(real)


def calcular_diferenca(real, previsto):
    """Diferença COM SINAL = observada - prevista.

    Positivo => latência ACIMA do previsto (pior). Negativo => abaixo do previsto.
    O erro absoluto perde essa informação, por isso guardamos a diferença também.
    """
    return real - previsto


def classificar_direcao(diferenca, tolerancia=0.005):
    """Devolve 'acima', 'abaixo' ou 'igual' (com tolerância por causa do ponto flutuante)."""
    if math.isclose(diferenca, 0.0, abs_tol=tolerancia):
        return "igual"
    return "acima" if diferenca > 0 else "abaixo"


def adicionar_erros(df):
    """Cria erro_absoluto, erro_relativo e diferenca_ms, linha por linha (módulo a módulo).

    Os valores são arredondados só na hora de guardar (2 casas em ms, 4 casas na fração),
    para não aparecer sujeira de ponto flutuante como 0.9299999999999997.
    """
    df = df.copy()
    df["erro_absoluto"] = df.apply(
        lambda linha: calcular_erro_absoluto(linha[COLUNA_REAL], linha[COLUNA_PREVISTA]),
        axis=1,
    ).round(2)
    df["erro_relativo"] = pd.to_numeric(
        df.apply(
            lambda linha: calcular_erro_relativo(linha[COLUNA_REAL], linha[COLUNA_PREVISTA]),
            axis=1,
        ),
        errors="coerce",  # None (divisão por zero) vira NaN
    ).round(4)
    df["diferenca_ms"] = df.apply(
        lambda linha: calcular_diferenca(linha[COLUNA_REAL], linha[COLUNA_PREVISTA]),
        axis=1,
    ).round(2)
    return df


# ---------------------------------------------------------------------------
# 2. Método de Euler: atenuação de sinal ao longo do tempo
# ---------------------------------------------------------------------------
def simular_atenuacao_euler(sinal_inicial=100.0, k=0.3, passo=0.5, n_passos=20):
    """Simula dy/dt = -k * y  (o sinal perde força proporcionalmente ao que ainda tem).

    Euler: y_novo = y_atual + passo * (-k * y_atual)
    Também calcula a solução exata y(t) = y0 * e^(-k*t) para medir o erro do método.
    """
    historico = []
    y = sinal_inicial
    for i in range(n_passos + 1):
        t = i * passo
        y_exato = sinal_inicial * math.exp(-k * t)
        historico.append(
            {
                "tempo": t,
                "sinal_euler": y,
                "sinal_exato": y_exato,
                "erro_absoluto": calcular_erro_absoluto(y_exato, y),
            }
        )
        y = y + passo * (-k * y)  # o "passinho" do Euler
    return historico


# ---------------------------------------------------------------------------
# 3. Ponto flutuante (IEEE 754)
# ---------------------------------------------------------------------------
def demonstrar_ponto_flutuante():
    """Mostra que 0.1 + 0.2 não é exatamente 0.3 no computador e como comparar direito."""
    soma = 0.1 + 0.2
    return {
        "soma": soma,
        "soma_com_17_casas": f"{soma:.17f}",
        "igualdade_direta": soma == 0.3,  # False!
        "igualdade_com_tolerancia": math.isclose(soma, 0.3, rel_tol=1e-9),  # True
    }


# ---------------------------------------------------------------------------
# 4. Severidade do alerta (1 a 5)
# ---------------------------------------------------------------------------
def _normalizar_status(status):
    """Deixa o status em minúsculas e sem acento/espaços: 'Manutenção ' -> 'manutencao'."""
    texto = str(status).strip().lower()
    return texto.replace("ç", "c").replace("ã", "a")


def calcular_severidade(erro_relativo, status):
    """Regra: severidade base pelo erro relativo + bônus pelo status, limitada a 1..5."""
    if erro_relativo is None or pd.isna(erro_relativo):
        base = 5  # sem como avaliar o erro = cenário mais cauteloso
    else:
        base = 5
        for limite, nivel in FAIXAS_ERRO_RELATIVO:
            if erro_relativo < limite:
                base = nivel
                break

    bonus = BONUS_STATUS.get(_normalizar_status(status), 0)
    return max(1, min(5, base + bonus))


def adicionar_severidade(df):
    """Cria a coluna severidade_alerta (int de 1 a 5) no DataFrame."""
    df = df.copy()
    df["severidade_alerta"] = df.apply(
        lambda linha: calcular_severidade(linha["erro_relativo"], linha["status"]),
        axis=1,
    )
    return df


# ---------------------------------------------------------------------------
# 5. Lista de alertas (entrada do AlertHeap da Semana 4)
# ---------------------------------------------------------------------------
def _montar_mensagem(linha, direcao):
    """Texto curto do alerta, dizendo se a latência está acima ou abaixo do previsto."""
    if pd.isna(linha["erro_relativo"]):
        detalhe = "erro relativo indefinido"
    else:
        detalhe = f"{linha['erro_relativo'] * 100:.1f}% de erro"
    if direcao == "igual":
        posicao = "igual ao previsto"
    else:
        posicao = f"{abs(linha['diferenca_ms']):.1f} ms {direcao} do previsto"
    return f"{linha['modulo_nome']}: latência {posicao} ({detalhe}, status: {linha['status']})"


def gerar_alertas(df, severidade_minima=3):
    """Devolve a lista de dicionários com os alertas operacionais.

    Ordem: maior severidade primeiro; empate resolvido pela prioridade do módulo
    (1 = mais essencial) e, por fim, pelo maior erro absoluto.
    """
    tem_prioridade = "prioridade" in df.columns
    alertas = []
    for _, linha in df.iterrows():
        if linha["severidade_alerta"] >= severidade_minima:
            direcao = classificar_direcao(linha["diferenca_ms"])
            alertas.append(
                {
                    "modulo_nome": linha["modulo_nome"],
                    "sensor_hex_id": linha["sensor_hex_id"],
                    "status": linha["status"],
                    "erro_absoluto": float(linha["erro_absoluto"]),
                    "erro_relativo": float(linha["erro_relativo"]),
                    "severidade_alerta": int(linha["severidade_alerta"]),
                    "diferenca_ms": float(linha["diferenca_ms"]),
                    "direcao": direcao,
                    "prioridade": int(linha["prioridade"]) if tem_prioridade else PRIORIDADE_PADRAO,
                    "mensagem": _montar_mensagem(linha, direcao),
                }
            )
    alertas.sort(key=lambda a: (-a["severidade_alerta"], a["prioridade"], -a["erro_absoluto"]))
    return alertas


def filtrar_acima_do_previsto(alertas):
    """Só os alertas com latência ACIMA do previsto (o caso mais preocupante da colônia)."""
    return [a for a in alertas if a["direcao"] == "acima"]


# ---------------------------------------------------------------------------
# Pipeline completo: CSV entra, CSV enriquecido + alertas saem
# ---------------------------------------------------------------------------
def processar_dataset(caminho_csv=CAMINHO_CSV, salvar=True):
    """Lê o CSV da Semana 2, calcula erros e severidade, salva e devolve (df, alertas)."""
    # utf-8-sig remove o BOM que o Excel coloca no começo do arquivo
    df = pd.read_csv(caminho_csv, encoding="utf-8-sig")

    df = adicionar_erros(df)
    df = adicionar_severidade(df)
    alertas = gerar_alertas(df)

    if salvar:
        df.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
    return df, alertas


# ---------------------------------------------------------------------------
# Testes rápidos (rodam só quando o arquivo é executado direto)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== 1. Erros (real=100 ms, previsto=95 ms) ===")
    print("Absoluto:", calcular_erro_absoluto(100, 95))  # 5
    print("Relativo:", calcular_erro_relativo(100, 95))  # 0.05 (5%)
    print("Diferença com sinal:", calcular_diferenca(100, 95), "->", classificar_direcao(5))  # acima

    print("\n=== 2. Ponto flutuante ===")
    for chave, valor in demonstrar_ponto_flutuante().items():
        print(f"{chave}: {valor}")

    print("\n=== 3. Euler (primeiros 5 passos) ===")
    for ponto in simular_atenuacao_euler()[:5]:
        print(
            f"t={ponto['tempo']:.1f} | euler={ponto['sinal_euler']:.3f} | "
            f"exato={ponto['sinal_exato']:.3f} | erro={ponto['erro_absoluto']:.3f}"
        )

    print("\n=== 4. Severidade ===")
    print("erro 3%  + ativo      ->", calcular_severidade(0.03, "ativo"))  # 1
    print("erro 15% + manutenção ->", calcular_severidade(0.15, "Manutenção"))  # 4
    print("erro 50% + alerta     ->", calcular_severidade(0.50, "alerta"))  # 5 (limitado)

    print("\n=== 5. Pipeline completo (sem sobrescrever o CSV) ===")
    try:
        tabela, lista_alertas = processar_dataset(salvar=False)
        print(tabela[["modulo_nome", "erro_absoluto", "erro_relativo", "diferenca_ms", "severidade_alerta"]].head())
        acima = filtrar_acima_do_previsto(lista_alertas)
        print(f"\n{len(lista_alertas)} alertas gerados ({len(acima)} com latência acima do previsto).")
        if lista_alertas:
            print("Mais crítico:", lista_alertas[0]["mensagem"])
    except FileNotFoundError:
        print("dados_aurora_siger.csv não encontrado nesta pasta, pulei este teste.")