import csv

def converter_id(sensor_hex_id):
    decimal = int(sensor_hex_id, 16)        # hex -> decimal
    binario = bin(decimal).replace("0b", "")  # decimal -> binário

    print(f"  Hex:     {sensor_hex_id}")
    print(f"  Decimal: {decimal}")
    print(f"  Binário: {binario}")

def calcular_eletrico(nome, tensao, corrente):
    potencia    = tensao * corrente
    resistencia = tensao / corrente

    print(f"  Módulo:      {nome}")
    print(f"  Tensão:      {tensao} V")
    print(f"  Corrente:    {corrente} A")
    print(f"  Potência:    {round(potencia, 2)} W")
    print(f"  Resistência: {round(resistencia, 2)} Ω")

def mostrar_conversoes():
    print("\n=== CONVERSÃO DE BASES — SENSORES DA COLÔNIA ===")

    with open("dados_aurora_siger.csv", "r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            print(f"\n  [{linha['modulo_nome']}]")
            converter_id(linha["sensor_hex_id"])


def mostrar_calculos():
    print("\n=== ANÁLISE ELÉTRICA — MÓDULOS DA COLÔNIA ===")

    with open("dados_aurora_siger.csv", "r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            print()
            calcular_eletrico(
                nome     = linha["modulo_nome"],
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
