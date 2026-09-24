"""
Script de Testes Unitários e Validação do Módulo de Machine Learning (Semana 2)
Responsável: Aelton (Membro 2)
"""

from ml_model import (
    carregar_dados,
    preparar_dados,
    treinar_modelo,
    calcular_metricas,
    executar_pipeline_completo
)

print("=== TESTE 1: Carga dos Dados e Integridade do Dataset ===")
df = carregar_dados("dados_aurora_siger.csv")
print(f"✓ Registros carregados: {len(df)}")
assert len(df) > 0, "O dataset não pode estar vazio"
assert "latencia_observada_ms" in df.columns, "Coluna latencia_observada_ms obrigatória"
print("✓ Validação de colunas concluída com sucesso.")

print("\n=== TESTE 2: Partição Treino/Teste e Treinamento do Modelo ===")
X_train, X_test, y_train, y_test, X_full, y_full = preparar_dados(df)
print(f"✓ Formato Treino: {X_train.shape} | Formato Teste: {X_test.shape}")
modelo = treinar_modelo(X_train, y_train)
assert hasattr(modelo, "coef_"), "O modelo precisa possuir coeficientes ajustados"
print(f"✓ Coeficientes ajustados: {modelo.coef_}")
print(f"✓ Intercepto: {modelo.intercept_:.4f}")

print("\n=== TESTE 3: Cálculo e Validação das 4 Métricas Obrigatórias ===")
y_pred_test = modelo.predict(X_test)
metricas = calcular_metricas(y_test, y_pred_test)
print(f"✓ MAE:  {metricas['MAE']} ms")
print(f"✓ MSE:  {metricas['MSE']} ms²")
print(f"✓ RMSE: {metricas['RMSE']} ms")
print(f"✓ R²:   {metricas['R2']}")
for m in ["MAE", "MSE", "RMSE", "R2"]:
    assert m in metricas, f"Métrica {m} não encontrada no retorno"

print("\n=== TESTE 4: Execução do Pipeline Completo e Enriquecimento do CSV ===")
resultado = executar_pipeline_completo(exibir_detalhes=False)
assert "latencia_prevista_ms" in resultado["dataframe"].columns, "Coluna latencia_prevista_ms deve estar no DataFrame final"
print(f"✓ Coluna 'latencia_prevista_ms' gerada com sucesso.")
print(f"✓ Total de gráficos gerados: {len(resultado['graficos'])}")

print("\n=== TODOS OS TESTES DE MACHINE LEARNING CONCLUÍDOS COM SUCESSO! ===")
