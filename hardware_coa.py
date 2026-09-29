"""
hardware_coa.py - SCIC / Aurora Siger (Semana 1)

Arquitetura de Computadores aplicada à colônia:
  1. Conversão de bases numéricas (hexadecimal -> decimal -> binário) dos IDs dos sensores
  2. Eletricidade básica: potência (P = V x I) e resistência (R = V / I) de cada módulo

Regra deste módulo: as funções de CÁLCULO devolvem valores (return) e as funções de
EXIBIÇÃO é que imprimem. Assim o menu do codigo_fonte.py pode reaproveitar os resultados.
"""

import csv
import os

# Caminho do CSV ancorado na pasta deste arquivo: funciona mesmo se o programa
# for executado de outra pasta (ex.: python pasta/codigo_fonte.py).
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(PASTA_PROJETO, "dados_aurora_siger.csv")


# ---------------------------------------------------------------------------
# 1. Funções de cálculo (não imprimem nada, só devolvem)
# ---------------------------------------------------------------------------
def converter_id(sensor_hex_id):
    """Converte o ID hexadecimal de um sensor. Devolve um dicionário com as 3 bases."""
    decimal = int(str(sensor_hex_id).strip(), 16)  # hex -> decimal (aceita o prefixo 0x)
    return {
        "hex": "0x" + format(decimal, "X"),        # hex padronizado: 0xA1F3
        "decimal": decimal,
        "binario": format(decimal, "b"),           # decimal -> binário (sem o 0b)
    }


def calcular_eletrico(nome, tensao, corrente):
    """Lei de Ohm: P = V x I (potência em W) e R = V / I (resistência em ohms).

    Se a corrente for 0 não dá para calcular a resistência, então devolvemos None
    (mesma ideia usada no erro relativo da Semana 3).
    """
    potencia = tensao * corrente
    resistencia = None if corrente == 0 else tensao / corrente
    return {
        "modulo": nome,
        "tensao_v": tensao,
        "corrente_a": corrente,
        "potencia_w": potencia,
        "resistencia_ohm": resistencia,
    }


def carregar_linhas(caminho=CAMINHO_CSV):
    """Lê o CSV e devolve uma lista de dicionários (uma por registro)."""
    # utf-8-sig remove o BOM que a Semana 3 grava no começo do arquivo
    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def _primeiro_por_modulo(linhas):
    """Mantém só o primeiro registro de cada módulo (evita imprimir 80 blocos)."""
    vistos, resultado = set(), []
    for linha in linhas:
        if linha["modulo_nome"] not in vistos:
            vistos.add(linha["modulo_nome"])
            resultado.append(linha)
    return resultado


# ---------------------------------------------------------------------------
# 2. Funções de exibição (só imprimem)
# ---------------------------------------------------------------------------
def exibir_conversao(resultado):
    print(f"  Hex:     {resultado['hex']}")
    print(f"  Decimal: {resultado['decimal']}")
    print(f"  Binário: {resultado['binario']}")


def exibir_eletrico(resultado):
    resistencia = resultado["resistencia_ohm"]
    texto_r = "indefinida (corrente = 0)" if resistencia is None else f"{resistencia:.2f} Ω"
    print(f"  Módulo:      {resultado['modulo']}")
    print(f"  Tensão:      {resultado['tensao_v']} V")
    print(f"  Corrente:    {resultado['corrente_a']} A")
    print(f"  Potência:    {resultado['potencia_w']:.2f} W")
    print(f"  Resistência: {texto_r}")


def mostrar_conversoes(todos=False):
    """Mostra a conversão de bases. Por padrão, 1 sensor por módulo; todos=True mostra tudo."""
    print("\n=== CONVERSÃO DE BASES - SENSORES DA COLÔNIA ===")
    linhas = carregar_linhas()
    if not todos:
        linhas = _primeiro_por_modulo(linhas)
    for linha in linhas:
        print(f"\n  [{linha['modulo_nome']}]")
        exibir_conversao(converter_id(linha["sensor_hex_id"]))


def mostrar_calculos(todos=False):
    """Mostra potência e resistência. Por padrão, 1 registro por módulo."""
    print("\n=== ANÁLISE ELÉTRICA - MÓDULOS DA COLÔNIA ===")
    linhas = carregar_linhas()
    if not todos:
        linhas = _primeiro_por_modulo(linhas)
    for linha in linhas:
        print()
        exibir_eletrico(
            calcular_eletrico(
                nome=linha["modulo_nome"],
                tensao=float(linha["tensao_v"]),
                corrente=float(linha["corrente_a"]),
            )
        )


# ---------------------------------------------------------------------------
# Menu do módulo (uso isolado)
# ---------------------------------------------------------------------------
def menu():
    while True:
        print("\n=== HARDWARE COA - Aurora Siger ===")
        print("1 - Converter IDs dos sensores")
        print("2 - Calcular potência e resistência")
        print("3 - Executar tudo")
        print("4 - Ver todos os registros (conversão + cálculo)")
        print("0 - Sair")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            mostrar_conversoes()
        elif opcao == "2":
            mostrar_calculos()
        elif opcao == "3":
            mostrar_conversoes()
            mostrar_calculos()
        elif opcao == "4":
            mostrar_conversoes(todos=True)
            mostrar_calculos(todos=True)
        elif opcao == "0":
            print("Encerrando.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()