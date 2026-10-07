"""
teste_hardware.py - Testes do módulo hardware_coa (Semana 1)
Agora com assert: se algo estiver errado, o teste FALHA (antes só imprimia "sucesso").
"""

import math
import os

from hardware_coa import CAMINHO_CSV, calcular_eletrico, carregar_linhas, converter_id

print("=== TESTE 1: Conversão de bases ===")
r = converter_id("0xA1F3")
assert r["decimal"] == 41459, "0xA1F3 deve valer 41459 em decimal"
assert r["binario"] == "1010000111110011", "Binário de 0xA1F3 incorreto"
assert r["hex"] == "0xA1F3", "Hex deve voltar padronizado"
assert converter_id("0xb2c4")["decimal"] == 0xB2C4, "Deve aceitar minúsculas"
assert converter_id("C3D5")["decimal"] == 0xC3D5, "Deve aceitar sem o prefixo 0x"
print("✓ 0xA1F3 = 41459 = 1010000111110011 (hex, decimal e binário conferem)")

print("\n=== TESTE 2: Cálculo elétrico (Lei de Ohm) ===")
e = calcular_eletrico("Suporte Vital", 12.0, 3.8)
# Atenção: 12.0 * 3.8 dá 45.599999999999994 (ponto flutuante), então NÃO usamos ==
assert math.isclose(e["potencia_w"], 45.6, rel_tol=1e-9), "P = 12 x 3.8 deve ser 45.6 W"
assert math.isclose(e["resistencia_ohm"], 12.0 / 3.8, rel_tol=1e-9), "R = V / I incorreta"
assert calcular_eletrico("Energia", 24.0, 8.5)["potencia_w"] == 204.0, "P = 24 x 8.5 = 204 W"
print(f"✓ P = {e['potencia_w']:.2f} W | R = {e['resistencia_ohm']:.2f} Ω")

print("\n=== TESTE 3: Corrente zero (divisão por zero) ===")
zero = calcular_eletrico("Teste", 12.0, 0)
assert zero["resistencia_ohm"] is None, "Corrente 0 deve devolver resistência None"
assert zero["potencia_w"] == 0, "Potência com corrente 0 deve ser 0"
print("✓ Divisão por zero tratada (resistência = None)")

print("\n=== TESTE 4: Leitura do CSV ===")
if os.path.exists(CAMINHO_CSV):
    linhas = carregar_linhas()
    assert len(linhas) > 0, "O CSV não pode estar vazio"
    for coluna in ["modulo_nome", "sensor_hex_id", "tensao_v", "corrente_a"]:
        assert coluna in linhas[0], f"Coluna {coluna} ausente no CSV"
    print(f"✓ {len(linhas)} registros lidos com as colunas necessárias")
else:
    print("(dados_aurora_siger.csv não encontrado nesta pasta, pulei este teste)")

print("\n=== TODOS OS TESTES DE HARDWARE CONCLUÍDOS COM SUCESSO! ===")