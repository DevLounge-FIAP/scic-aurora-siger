from hardware_coa import converter_id, calcular_eletrico

print("=== TESTE 1: Conversão de bases ===")
print("\nSensor do módulo Suporte Vital:")
converter_id("0xA1F3")

print("\nSensor do módulo Energia:")
converter_id("0xB2C4")

print("\nSensor do módulo Comunicacao:")
converter_id("0xC3D5")

print("\n=== TESTE 2: Cálculo elétrico ===")
print("\nMódulo Suporte Vital:")
calcular_eletrico("Suporte Vital", 12.0, 3.8)

print("\nMódulo Energia:")
calcular_eletrico("Energia", 24.0, 8.5)

print("\nMódulo Habitat:")
calcular_eletrico("Habitat", 12.0, 2.5)

print("\n=== Todos os testes concluídos com sucesso! ===")