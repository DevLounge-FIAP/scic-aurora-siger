import csv

def converter_id(id_sensor):
    """Converte o ID do sensor de hex para decimal e binário."""

    decimal = int(id_sensor, 16)        # hex -> decimal
    binario = bin(decimal).replace("0b", "")  # decimal -> binário

    print(f"  Hex:     {id_sensor}")
    print(f"  Decimal: {decimal}")
    print(f"  Binário: {binario}")

def calcular_eletrico(nome, tensao, corrente):
    """Calcula e exibe potência e resistência de um módulo."""

    potencia    = tensao * corrente
    resistencia = tensao / corrente

    print(f"  Módulo:      {nome}")
    print(f"  Tensão:      {tensao} V")
    print(f"  Corrente:    {corrente} A")
    print(f"  Potência:    {round(potencia, 2)} W")
    print(f"  Resistência: {round(resistencia, 2)} Ω")

def mostrar_conversoes():
    """Lê o CSV e converte o ID de cada sensor."""

    print("\n=== CONVERSÃO DE BASES — SENSORES DA COLÔNIA ===")

    with open("dados_aurora_siger.csv", "r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            print(f"\n  [{linha['nome_modulo']}]")
            converter_id(linha["id_sensor"])


def mostrar_calculos():
    """Lê o CSV e calcula a parte elétrica de cada módulo."""

    print("\n=== ANÁLISE ELÉTRICA — MÓDULOS DA COLÔNIA ===")

    with open("dados_aurora_siger.csv", "r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            print()
            calcular_eletrico(
                nome     = linha["nome_modulo"],
                tensao   = float(linha["tensao_v"]),
                corrente = float(linha["corrente_a"]),
            )

def menu():
    while True:
        print("\n=== HARDWARE COA — Aurora Siger ===")
        print("1 - Converter IDs dos sensores")
        print("2 - Calcular potência e resistência")
        print("3 - Executar tudo")
        print("0 - Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            mostrar_conversoes()
        elif opcao == "2":
            mostrar_calculos()
        elif opcao == "3":
            mostrar_conversoes()
            mostrar_calculos()
        elif opcao == "0":
            print("Encerrando.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
