"""
Script de Testes e Validação do Módulo de Análise Numérica (Semana 3)
Cobre: erros absoluto/relativo, Euler, ponto flutuante, severidade, lista de alertas,
erro com sinal (acima/abaixo do previsto) e desempate por prioridade.
"""

import pandas as pd

from numerical_analysis import (
    adicionar_erros,
    adicionar_severidade,
    calcular_diferenca,
    calcular_erro_absoluto,
    calcular_erro_relativo,
    calcular_severidade,
    classificar_direcao,
    demonstrar_ponto_flutuante,
    filtrar_acima_do_previsto,
    gerar_alertas,
    processar_dataset,
    simular_atenuacao_euler,
)

print("=== TESTE 1: Erro absoluto e relativo ===")
assert calcular_erro_absoluto(100, 95) == 5, "Erro absoluto de 100 vs 95 deve ser 5"
assert calcular_erro_absoluto(95, 100) == 5, "Erro absoluto não pode depender da ordem"
assert abs(calcular_erro_relativo(100, 95) - 0.05) < 1e-12, "Erro relativo de 100 vs 95 deve ser 0.05"
assert calcular_erro_relativo(0, 5) is None, "Valor real zero deve devolver None"
print("✓ Erro absoluto = 5 ms | Erro relativo = 5% | Divisão por zero tratada.")

print("\n=== TESTE 2: Método de Euler ===")
historico = simular_atenuacao_euler(sinal_inicial=100.0, k=0.3, passo=0.5, n_passos=20)
assert len(historico) == 21, "20 passos devem gerar 21 pontos (incluindo t=0)"
assert historico[0]["sinal_euler"] == 100.0, "O sinal deve começar no valor inicial"
assert abs(historico[1]["sinal_euler"] - 85.0) < 1e-9, "Primeiro passo de Euler deve dar 85.0"
sinais = [p["sinal_euler"] for p in historico]
assert all(a > b for a, b in zip(sinais, sinais[1:])), "O sinal deve diminuir a cada passo"
erro_grande = simular_atenuacao_euler(passo=0.5, n_passos=4)[-1]["erro_absoluto"]
erro_pequeno = simular_atenuacao_euler(passo=0.1, n_passos=20)[-1]["erro_absoluto"]
assert erro_pequeno < erro_grande, "Passo menor deve gerar menor erro no mesmo instante (t=2)"
print(f"✓ Sinal atenua de 100 para {sinais[-1]:.2f}.")
print(f"✓ Erro em t=2: {erro_grande:.3f} (passo 0.5) contra {erro_pequeno:.3f} (passo 0.1).")

print("\n=== TESTE 3: Ponto flutuante (IEEE 754) ===")
pf = demonstrar_ponto_flutuante()
assert pf["igualdade_direta"] is False, "0.1 + 0.2 não deve ser igual a 0.3"
assert pf["igualdade_com_tolerancia"] is True, "Com tolerância, deve ser considerado igual"
print(f"✓ 0.1 + 0.2 = {pf['soma']} (igualdade direta: False | com tolerância: True)")

print("\n=== TESTE 4: Severidade (escala de 1 a 5) ===")
assert calcular_severidade(0.03, "ativo") == 1
assert calcular_severidade(0.15, "Manutenção") == 4, "Status deve ser normalizado (acento/maiúscula)"
assert calcular_severidade(0.50, "alerta") == 5, "Severidade deve ser limitada em 5"
assert calcular_severidade(None, "ativo") == 5, "Erro indefinido deve ser tratado como pior caso"
for erro in [0.0, 0.049, 0.05, 0.1, 0.2, 0.35, 1.0, 10.0]:
    for status in ["ativo", "manutencao", "alerta", "desconhecido"]:
        assert 1 <= calcular_severidade(erro, status) <= 5, f"Fora de 1..5: {erro}, {status}"
print("✓ Severidade sempre entre 1 e 5 em todas as combinações de erro e status.")

print("\n=== TESTE 5: Pipeline com o dataset real (sem sobrescrever o CSV) ===")
df, alertas = processar_dataset(salvar=False)
for coluna in ["erro_absoluto", "erro_relativo", "severidade_alerta", "diferenca_ms"]:
    assert coluna in df.columns, f"Coluna {coluna} deve existir no DataFrame"
assert (df["erro_absoluto"] >= 0).all(), "Erro absoluto nunca é negativo"
assert df["severidade_alerta"].between(1, 5).all(), "Severidade deve estar entre 1 e 5"
assert len(alertas) > 0, "Deve existir ao menos um alerta"
chaves = {"modulo_nome", "sensor_hex_id", "status", "erro_absoluto",
          "erro_relativo", "severidade_alerta", "mensagem"}
assert all(chaves <= set(a.keys()) for a in alertas), "Todo alerta deve ter as chaves do contrato"
severidades = [a["severidade_alerta"] for a in alertas]
assert severidades == sorted(severidades, reverse=True), "Alertas devem vir do mais grave ao menos grave"
print(f"✓ {len(df)} registros processados | {len(alertas)} alertas gerados.")
print(f"✓ Alerta mais crítico: {alertas[0]['mensagem']} (severidade {alertas[0]['severidade_alerta']})")

print("\n=== TESTE 6: Erro com sinal (acima/abaixo do previsto) ===")
assert calcular_diferenca(100, 95) == 5 and classificar_direcao(5) == "acima"
assert calcular_diferenca(95, 100) == -5 and classificar_direcao(-5) == "abaixo"
assert classificar_direcao(0.0) == "igual"
assert classificar_direcao(0.1 + 0.2 - 0.3) == "igual", "Ruído de ponto flutuante deve contar como igual"
assert all(a["direcao"] in {"acima", "abaixo", "igual"} for a in alertas), "Todo alerta precisa de direção"
acima = filtrar_acima_do_previsto(alertas)
assert all(a["diferenca_ms"] > 0 for a in acima), "Filtro deve trazer só diferenças positivas"
print(f"✓ Direção correta | {len(acima)} de {len(alertas)} alertas estão acima do previsto.")

print("\n=== TESTE 7: Arredondamento e desempate por prioridade ===")
mini = pd.DataFrame({
    "modulo_nome": ["A", "B", "C"],
    "sensor_hex_id": ["0x01", "0x02", "0x03"],
    "status": ["alerta", "alerta", "ativo"],
    "latencia_observada_ms": [100.0, 100.0, 100.0],
    "latencia_prevista_ms": [110.0, 90.0, 100.0],
    "prioridade": [2, 1, 1],
})
mini = adicionar_severidade(adicionar_erros(mini))
assert mini["diferenca_ms"].tolist() == [-10.0, 10.0, 0.0], "Diferença com sinal incorreta"
assert list(mini["erro_absoluto"]) == [10.0, 10.0, 0.0], "Erro absoluto incorreto"
lista = gerar_alertas(mini)
assert [a["modulo_nome"] for a in lista] == ["B", "A"], "Empate de severidade: prioridade 1 vem antes da 2"
assert lista[0]["direcao"] == "acima" and lista[1]["direcao"] == "abaixo"
assert "acima do previsto" in lista[0]["mensagem"], "Mensagem deve dizer acima/abaixo"
assert (df["erro_absoluto"] == df["erro_absoluto"].round(2)).all(), "Erro absoluto deve estar com 2 casas"
print("✓ Desempate por prioridade OK | erros arredondados sem sujeira de ponto flutuante.")

print("\n=== TODOS OS TESTES DE ANÁLISE NUMÉRICA CONCLUÍDOS COM SUCESSO! ===")