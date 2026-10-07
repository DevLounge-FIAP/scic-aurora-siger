"""
Script de Testes Unitários e Validação do Módulo de Machine Learning (Semana 2)
Responsável: Aelton (Membro 2)

O pipeline completo (teste 6) roda sobre uma CÓPIA temporária do CSV, então este
teste não altera o dados_aurora_siger.csv nem os gráficos oficiais da entrega.
"""

import math
import os
import shutil
import tempfile

import pandas as pd

from ml_model import (
    ARQUIVO_DADOS_PADRAO,
    FEATURES_PADRAO,
    calcular_aic_bic,
    calcular_baseline,
    calcular_metricas,
    carregar_dados,
    comparar_modelos,
    executar_pipeline_completo,
    preparar_dados,
    treinar_modelo,
)

print("=== TESTE 1: Carga dos Dados e Integridade do Dataset ===")
df = carregar_dados()
print(f"✓ Registros carregados: {len(df)}")
assert len(df) > 0, "O dataset não pode estar vazio"
for coluna in FEATURES_PADRAO + ["latencia_observada_ms"]:
    assert coluna in df.columns, f"Coluna {coluna} obrigatória"
print("✓ Validação de colunas concluída com sucesso.")

print("\n=== TESTE 2: Partição Treino/Teste e Treinamento do Modelo ===")
X_train, X_test, y_train, y_test, X_full, y_full = preparar_dados(df)
assert len(X_train) + len(X_test) == len(df), "Treino + teste deve cobrir toda a base"
assert set(X_train.index).isdisjoint(X_test.index), "Treino e teste não podem compartilhar linhas"
X_train_2, X_test_2, _, _, _, _ = preparar_dados(df)
assert list(X_test.index) == list(X_test_2.index), "random_state fixo deve repetir a mesma divisão"
print(f"✓ Formato Treino: {X_train.shape} | Formato Teste: {X_test.shape} | divisão reprodutível")
modelo = treinar_modelo(X_train, y_train)
assert len(modelo.coef_) == len(FEATURES_PADRAO), "Um coeficiente por feature"
print(f"✓ Coeficientes ajustados: {modelo.coef_}")
print(f"✓ Intercepto: {modelo.intercept_:.4f}")

print("\n=== TESTE 3: Cálculo e Validação das 4 Métricas Obrigatórias ===")
perfeito = calcular_metricas([10.0, 20.0, 30.0], [10.0, 20.0, 30.0])
assert perfeito["MAE"] == 0 and perfeito["RMSE"] == 0 and perfeito["R2"] == 1, "Previsão perfeita: erro 0 e R² 1"
conhecido = calcular_metricas([10.0, 20.0], [12.0, 16.0])  # erros 2 e 4
assert conhecido["MAE"] == 3.0 and conhecido["MSE"] == 10.0, "MAE = (2+4)/2 = 3 | MSE = (4+16)/2 = 10"
assert math.isclose(conhecido["RMSE"], math.sqrt(10), abs_tol=1e-4), "RMSE = raiz do MSE"

metricas = calcular_metricas(y_test, modelo.predict(X_test))
for m in ["MAE", "MSE", "RMSE", "R2"]:
    assert m in metricas, f"Métrica {m} não encontrada no retorno"
assert metricas["RMSE"] >= metricas["MAE"], "RMSE nunca é menor que o MAE"
print(f"✓ MAE:  {metricas['MAE']} ms")
print(f"✓ MSE:  {metricas['MSE']} ms²")
print(f"✓ RMSE: {metricas['RMSE']} ms")
print(f"✓ R²:   {metricas['R2']}")

print("\n=== TESTE 4: Comparação com o Baseline (prever sempre a média) ===")
baseline = calcular_baseline(y_train, y_test)
assert abs(baseline["R2"]) < 0.05, "Baseline da média deve ter R² perto de zero"
assert metricas["MAE"] < baseline["MAE"], "A regressão precisa superar o baseline"
reducao = (1 - metricas["MAE"] / baseline["MAE"]) * 100
print(f"✓ Baseline MAE {baseline['MAE']} ms | modelo {metricas['MAE']} ms | redução de {reducao:.0f}%")

print("\n=== TESTE 5: Comparação de Modelos por AIC e BIC ===")
aic, bic = calcular_aic_bic(n=60, rss=60.0, k=3)  # ln(RSS/n) = ln(1) = 0
assert math.isclose(aic, 6.0) and math.isclose(bic, 3 * math.log(60)), "Fórmulas de AIC/BIC incorretas"
comparacao = comparar_modelos(df)
assert len(comparacao) == 3, "Devem ser comparados 3 conjuntos de variáveis"
melhor_aic = min(comparacao, key=lambda r: r["AIC"])["modelo"]
melhor_bic = min(comparacao, key=lambda r: r["BIC"])["modelo"]
assert "oficial" in melhor_aic and "oficial" in melhor_bic, "O modelo oficial deve ter o menor AIC e BIC"
for r in comparacao:
    print(f"  {r['modelo']:<30} AIC {r['AIC']:>7.2f} | BIC {r['BIC']:>7.2f}")
print("✓ O modelo oficial (tensão + corrente) vence pelo critério de parcimônia")

print("\n=== TESTE 6: Pipeline Completo em uma Cópia Temporária do CSV ===")
with tempfile.TemporaryDirectory() as pasta_temp:
    csv_temp = os.path.join(pasta_temp, "dados_aurora_siger.csv")
    shutil.copy(ARQUIVO_DADOS_PADRAO, csv_temp)
    resultado = executar_pipeline_completo(
        caminho_csv=csv_temp,
        pasta_graficos=os.path.join(pasta_temp, "graficos"),
        exibir_detalhes=False,
    )
    df_salvo = pd.read_csv(csv_temp)

    assert "latencia_prevista_ms" in df_salvo.columns, "CSV deve ganhar a coluna latencia_prevista_ms"
    assert df_salvo["latencia_prevista_ms"].notna().all(), "Todos os registros precisam de previsão"
    assert len(resultado["graficos"]) == 3, "Devem ser gerados 3 gráficos"
    assert all(os.path.exists(g) for g in resultado["graficos"]), "Os arquivos PNG precisam existir"
    for chave in ["metricas_teste", "metricas_baseline", "comparacao_modelos"]:
        assert chave in resultado, f"Resultado do pipeline sem a chave '{chave}'"
print("✓ Coluna 'latencia_prevista_ms' gerada para todos os registros.")
print(f"✓ Total de gráficos gerados: {len(resultado['graficos'])}")
print("✓ CSV e gráficos oficiais da entrega não foram alterados.")

print("\n=== TODOS OS TESTES DE MACHINE LEARNING CONCLUÍDOS COM SUCESSO! ===")
