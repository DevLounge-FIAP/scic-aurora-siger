"""
Módulo de Aprendizado de Máquina e Regressão Linear - Missão Aurora Siger (SCIC Fase 6)
Responsável: Aelton (Membro 2 - Semana 2)

Descrição:
    Este módulo implementa o pipeline de previsão de latência de transmissão dos módulos
    da colônia marciana Aurora Siger utilizando Regressão Linear com Scikit-Learn.
    Realiza a divisão entre dados de treino e teste, calcula obrigatoriamente as métricas
    MAE, MSE, RMSE e R², exporta gráficos de dispersão e análise de resíduos (conforme Figura 3
    do manual oficial) e atualiza o dataset oficial com a coluna calculada 'latencia_prevista_ms'.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Garante execução headless sem necessidade de display gráfico
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Configurações globais de estilo para visualização científica
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "figure.titlesize": 14
})

# Caminhos padrão do projeto
ARQUIVO_DADOS_PADRAO = "dados_aurora_siger.csv"
PASTA_GRAFICOS_PADRAO = "graficos_ou_imagens"
FEATURES_PADRAO = ["tensao_v", "corrente_a"]
TARGET_PADRAO = "latencia_observada_ms"


def carregar_dados(caminho_csv: str = ARQUIVO_DADOS_PADRAO) -> pd.DataFrame:
    """
    Carrega o dataset oficial da missão a partir do arquivo CSV.

    Args:
        caminho_csv (str): Caminho para o arquivo CSV de telemetria.

    Returns:
        pd.DataFrame: DataFrame contendo os registros da colônia.
    """
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo de dados não encontrado: '{caminho_csv}'")
    
    df = pd.read_csv(caminho_csv)
    
    colunas_obrigatorias = FEATURES_PADRAO + [TARGET_PADRAO]
    for col in colunas_obrigatorias:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória '{col}' ausente no arquivo '{caminho_csv}'")
            
    return df


def preparar_dados(
    df: pd.DataFrame,
    features: list = None,
    target: str = TARGET_PADRAO,
    test_size: float = None,
    random_state: int = 42
):
    """
    Separa features (variáveis independentes) e target (variável dependente),
    realizando a partição formal entre treino e teste.

    Args:
        df (pd.DataFrame): DataFrame completo.
        features (list): Lista com os nomes das colunas de entrada.
        target (str): Nome da coluna da variável dependente.
        test_size (float, opcional): Proporção do conjunto de teste (ajustado automaticamente se pequeno).
        random_state (int): Semente para garantia de reprodutibilidade experimental.

    Returns:
        tuple: (X_train, X_test, y_train, y_test, X, y)
    """
    if features is None:
        features = FEATURES_PADRAO

    X = df[features]
    y = df[target]

    n_amostras = len(df)
    
    # Ajuste automático de test_size para bases pequenas garantindo no mínimo 2 amostras de teste
    if test_size is None:
        if n_amostras <= 5:
            test_size = 0.4  # Para 5 amostras: 3 treino, 2 teste
        elif n_amostras <= 10:
            test_size = 0.3
        else:
            test_size = 0.25

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    return X_train, X_test, y_train, y_test, X, y


def treinar_modelo(X_train: pd.DataFrame, y_train: pd.Series) -> LinearRegression:
    """
    Ajusta o estimador de Regressão Linear com Scikit-Learn aos dados de treino.

    Args:
        X_train (pd.DataFrame): Dados de treinamento das features.
        y_train (pd.Series): Variável-alvo de treino.

    Returns:
        LinearRegression: Estimador treinado.
    """
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    return modelo


def calcular_metricas(y_real, y_pred) -> dict:
    """
    Calcula as quatro métricas obrigatórias da Fase 6: MAE, MSE, RMSE e R².

    Args:
        y_real: Valores reais observados.
        y_pred: Valores previstos pelo modelo.

    Returns:
        dict: Dicionário contendo os valores calculados de cada métrica.
    """
    mae = mean_absolute_error(y_real, y_pred)
    mse = mean_squared_error(y_real, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_real, y_pred)

    return {
        "MAE": round(float(mae), 4),
        "MSE": round(float(mse), 4),
        "RMSE": round(float(rmse), 4),
        "R2": round(float(r2), 4)
    }


def interpretar_metricas(metricas: dict, rotulo: str = "Conjunto de Teste") -> str:
    """
    Gera uma interpretação crítica das métricas calculadas, conforme
    exigência expressa da Seção 5.3 do manual oficial da Fase 6.

    Args:
        metricas (dict): Dicionário retornado por calcular_metricas.
        rotulo (str): Identificador do conjunto analisado.

    Returns:
        str: Texto formatado com a análise diagnóstica.
    """
    mae = metricas["MAE"]
    mse = metricas["MSE"]
    rmse = metricas["RMSE"]
    r2 = metricas["R2"]

    diferenca_rmse_mae = round(rmse - mae, 4)

    relatorio = []
    relatorio.append(f"\n=======================================================")
    relatorio.append(f"   AVALIAÇÃO DE PERFORMANCE - {rotulo.upper()}")
    relatorio.append(f"=======================================================")
    relatorio.append(f"  • MAE  (Erro Médio Absoluto):        {mae:.2f} ms")
    relatorio.append(f"  • MSE  (Erro Quadrático Médio):       {mse:.2f} ms²")
    relatorio.append(f"  • RMSE (Raiz do Erro Quadrático):    {rmse:.2f} ms")
    relatorio.append(f"  • R²   (Coeficiente de Determinação): {r2:.4f}")
    relatorio.append(f"-------------------------------------------------------")
    relatorio.append(f"  DIAGNÓSTICO CRÍTICO CONFORME MANUAL OFICIAL (SEC. 5.3):")
    
    if r2 >= 0.85:
        relatorio.append(f"  - O R² ({r2:.2f}) indica excelente capacidade de explicação da variabilidade da latência.")
    elif r2 >= 0.50:
        relatorio.append(f"  - O R² ({r2:.2f}) demonstra correlação moderada com as grandezas elétricas.")
    else:
        relatorio.append(f"  - O R² ({r2:.2f}) aponta que fatores operacionais adicionais influenciam a latência.")

    if diferenca_rmse_mae > 1.5:
        relatorio.append(
            f"  - ATENÇÃO: A disparidade entre RMSE ({rmse:.2f} ms) e MAE ({mae:.2f} ms) [Δ = {diferenca_rmse_mae:.2f} ms]"
            f"\n    evidencia a ocorrência de erros residuais expressivos em módulos específicos."
            f"\n    O RMSE penaliza com maior rigor anomalias críticas que ameaçam o enlace da colônia."
        )
    else:
        relatorio.append(f"  - Os erros residuais são homogêneos (RMSE próximo a MAE, sem desvios aberrantes).")
    relatorio.append(f"=======================================================\n")

    return "\n".join(relatorio)


def gerar_graficos(
    y_real,
    y_pred,
    nomes_modulos: list = None,
    pasta_saida: str = PASTA_GRAFICOS_PADRAO
) -> list:
    """
    Gera e exporta para a pasta designada os gráficos de performance exigidos:
    1. Gráfico de Dispersão: Valores Reais vs. Valores Previstos (com linha ideal y = x).
    2. Gráfico de Análise de Resíduos: Dispersão dos resíduos (y - y_hat) com linha zero.
    3. Painel Integrado de Performance Operacional (Figura 3 do manual).

    Args:
        y_real: Vetor de valores observados.
        y_pred: Vetor de valores preditos.
        nomes_modulos (list, opcional): Nomes dos módulos para anotação.
        pasta_saida (str): Pasta de destino das imagens.

    Returns:
        list: Lista de caminhos dos arquivos de imagem gerados.
    """
    os.makedirs(pasta_saida, exist_ok=True)
    caminhos_gerados = []

    y_real = np.array(y_real)
    y_pred = np.array(y_pred)
    residuos = y_real - y_pred

    # -------------------------------------------------------------
    # 1. Gráfico de Dispersão: Reais vs. Previstos
    # -------------------------------------------------------------
    caminho_dispersao = os.path.join(pasta_saida, "dispersao_real_previsto.png")
    fig, ax = plt.subplots(figsize=(7, 6))

    ax.scatter(y_real, y_pred, color="#1f77b4", s=90, edgecolor="black", alpha=0.85, zorder=5, label="Módulos da Colônia")
    
    # Linha ideal de 45 graus (y = x)
    min_val = min(y_real.min(), y_pred.min()) - 3
    max_val = max(y_real.max(), y_pred.max()) + 3
    ax.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=1.8, label="Predição Ideal (y = x)", zorder=4)

    # Anotações dos módulos se fornecido (anota apenas os módulos representativos se N > 15)
    if nomes_modulos is not None and len(nomes_modulos) == len(y_real):
        if len(y_real) <= 15:
            indices_anotar = range(len(y_real))
        else:
            modulos_vistos = set()
            indices_anotar = []
            for idx, mod in enumerate(nomes_modulos):
                if mod not in modulos_vistos:
                    indices_anotar.append(idx)
                    modulos_vistos.add(mod)

        for i in indices_anotar:
            nome = nomes_modulos[i]
            ax.annotate(
                nome,
                (y_real[i], y_pred[i]),
                xytext=(8, -4),
                textcoords="offset points",
                fontsize=8.5,
                weight="bold",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.8, edgecolor="#999999")
            )

    ax.set_title("Calibração de Latência: Valores Observados vs. Previstos\nSCIC - Missão Aurora Siger", pad=12)
    ax.set_xlabel("Latência Observada (ms)")
    ax.set_ylabel("Latência Prevista (ms)")
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    
    fig.tight_layout()
    fig.savefig(caminho_dispersao, dpi=300)
    plt.close(fig)
    caminhos_gerados.append(caminho_dispersao)

    # -------------------------------------------------------------
    # 2. Gráfico de Análise de Resíduos
    # -------------------------------------------------------------
    caminho_residuos = os.path.join(pasta_saida, "analise_residuos.png")
    fig, ax = plt.subplots(figsize=(7, 5))

    ax.axhline(0, color="red", linestyle="--", linewidth=1.5, label="Resíduo Zero (Erro Nulo)", zorder=3)
    ax.scatter(y_pred, residuos, color="#d62728", s=85, edgecolor="black", alpha=0.85, zorder=5, label=r"Resíduo ($y - \hat{y}$)")

    if nomes_modulos is not None and len(nomes_modulos) == len(y_real):
        if len(y_real) <= 15:
            indices_res = range(len(y_real))
        else:
            modulos_vistos = set()
            indices_res = []
            for idx, mod in enumerate(nomes_modulos):
                if mod not in modulos_vistos:
                    indices_res.append(idx)
                    modulos_vistos.add(mod)

        for i in indices_res:
            nome = nomes_modulos[i]
            ax.annotate(
                f"{nome} ({residuos[i]:+.1f} ms)",
                (y_pred[i], residuos[i]),
                xytext=(8, 5 if residuos[i] >= 0 else -14),
                textcoords="offset points",
                fontsize=8.5,
                weight="bold",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.8, edgecolor="#999999")
            )

    ax.set_title("Análise de Resíduos da Regressão Linear\nDistribuição do Erro Residual por Nível de Latência", pad=12)
    ax.set_xlabel("Latência Prevista (ms)")
    ax.set_ylabel("Resíduo: Observada - Prevista (ms)")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)

    fig.tight_layout()
    fig.savefig(caminho_residuos, dpi=300)
    plt.close(fig)
    caminhos_gerados.append(caminho_residuos)

    # -------------------------------------------------------------
    # 3. Painel Integrado de Performance Operacional (Painel da Figura 3)
    # -------------------------------------------------------------
    caminho_painel = os.path.join(pasta_saida, "painel_performance_ml.png")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    # Painel 1: Dispersão
    ax1.scatter(y_real, y_pred, color="#2ca02c", s=80, edgecolor="black", zorder=5, label="Módulos")
    ax1.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=1.6, label="Ideal ($y = x$)")
    ax1.set_title("A) Dispersão Observada vs. Prevista")
    ax1.set_xlabel("Latência Observada (ms)")
    ax1.set_ylabel("Latência Prevista (ms)")
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Painel 2: Resíduos
    ax2.axhline(0, color="black", linestyle="--", linewidth=1.4, label="Linha Neutra")
    ax2.scatter(y_pred, residuos, color="#ff7f0e", s=80, edgecolor="black", zorder=5, label="Resíduos")
    ax2.set_title(r"B) Análise de Resíduos ($e = y - \hat{y}$)")
    ax2.set_xlabel("Latência Prevista (ms)")
    ax2.set_ylabel("Resíduo (ms)")
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle=":", alpha=0.6)

    fig.suptitle("Painel de Avaliação da Performance Operacional - SCIC Aurora Siger", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(caminho_painel, dpi=300)
    plt.close(fig)
    caminhos_gerados.append(caminho_painel)

    return caminhos_gerados


def atualizar_dataset(
    modelo: LinearRegression,
    df: pd.DataFrame,
    features: list = None,
    caminho_saida: str = ARQUIVO_DADOS_PADRAO
) -> pd.DataFrame:
    """
    Executa a inferência preditiva sobre todo o dataset e grava a nova
    coluna 'latencia_prevista_ms' no arquivo CSV oficial, preservando as
    demais colunas para consumo das semanas seguintes (Semana 3).

    Args:
        modelo (LinearRegression): Modelo treinado.
        df (pd.DataFrame): DataFrame completo.
        features (list): Features utilizadas.
        caminho_saida (str): Destino do arquivo CSV.

    Returns:
        pd.DataFrame: DataFrame atualizado com a coluna adicionada.
    """
    if features is None:
        features = FEATURES_PADRAO

    df_atualizado = df.copy()
    previsoes = modelo.predict(df_atualizado[features])
    df_atualizado["latencia_prevista_ms"] = np.round(previsoes, 2)

    df_atualizado.to_csv(caminho_saida, index=False, encoding="utf-8")
    return df_atualizado


def executar_pipeline_completo(
    caminho_csv: str = ARQUIVO_DADOS_PADRAO,
    pasta_graficos: str = PASTA_GRAFICOS_PADRAO,
    exibir_detalhes: bool = True
) -> dict:
    """
    Função mestra que orquestra todo o fluxo da Semana 2:
    1. Carga dos dados;
    2. Partição treino/teste;
    3. Treinamento da regressão linear;
    4. Avaliação e interpretação das métricas (MAE, MSE, RMSE, R²);
    5. Geração dos gráficos operacionais;
    6. Atualização do CSV com a nova coluna 'latencia_prevista_ms'.

    Esta função foi concebida para ser chamada tanto localmente quanto
    pelo integrador geral da equipe ('codigo_fonte.py' do Membro 5).

    Returns:
        dict: Resumo executivo contendo modelo, métricas, imagens e dataframe.
    """
    if exibir_detalhes:
        print("\n=======================================================")
        print("  INICIANDO PIPELINE DE MACHINE LEARNING - SEMANA 2")
        print("  Missão Aurora Siger - Regressão Linear de Latência")
        print("=======================================================")

    # 1. Carga
    df = carregar_dados(caminho_csv)
    if exibir_detalhes:
        print(f"✓ Base '{caminho_csv}' carregada com sucesso ({len(df)} registros).")

    # 2. Preparação
    X_train, X_test, y_train, y_test, X_full, y_full = preparar_dados(df)
    if exibir_detalhes:
        print(f"✓ Divisão dos dados: {len(X_train)} amostras de Treino | {len(X_test)} amostras de Teste.")

    # 3. Treinamento
    modelo = treinar_modelo(X_train, y_train)
    coef_str = ", ".join([f"{feat}: {coef:+.3f}" for feat, coef in zip(FEATURES_PADRAO, modelo.coef_)])
    if exibir_detalhes:
        print(f"✓ Modelo de Regressão Linear treinado.")
        print(f"  • Intercepto (β0): {modelo.intercept_:.3f}")
        print(f"  • Coeficientes (β): {coef_str}")

    # 4. Avaliação
    y_pred_test = modelo.predict(X_test)
    metricas_teste = calcular_metricas(y_test, y_pred_test)

    # Avaliação sobre base completa para o painel de telemetria
    y_pred_full = modelo.predict(X_full)
    metricas_completo = calcular_metricas(y_full, y_pred_full)

    if exibir_detalhes:
        print(interpretar_metricas(metricas_teste, rotulo="Conjunto de Teste"))
        print(f"Métricas globais no dataset completo:")
        print(f"  MAE: {metricas_completo['MAE']} ms | RMSE: {metricas_completo['RMSE']} ms | R²: {metricas_completo['R2']}")

    # 5. Gráficos
    nomes_modulos = df["modulo_nome"].tolist() if "modulo_nome" in df.columns else None
    graficos_salvos = gerar_graficos(
        y_real=y_full,
        y_pred=y_pred_full,
        nomes_modulos=nomes_modulos,
        pasta_saida=pasta_graficos
    )
    if exibir_detalhes:
        print(f"\n✓ Gráficos exportados com sucesso para '{pasta_graficos}/':")
        for g in graficos_salvos:
            print(f"  • {g}")

    # 6. Atualização do CSV oficial
    df_atualizado = atualizar_dataset(modelo, df, caminho_saida=caminho_csv)
    if exibir_detalhes:
        print(f"\n✓ Arquivo '{caminho_csv}' enriquecido com a coluna 'latencia_prevista_ms'.")
        print("\nVisualização dos dados atualizados:")
        cols_mostrar = ["modulo_nome", "tensao_v", "corrente_a", "latencia_observada_ms", "latencia_prevista_ms"]
        cols_disponiveis = [c for c in cols_mostrar if c in df_atualizado.columns]
        print(df_atualizado[cols_disponiveis].to_string(index=False))
        print("=======================================================\n")

    return {
        "modelo": modelo,
        "metricas_teste": metricas_teste,
        "metricas_completo": metricas_completo,
        "graficos": graficos_salvos,
        "dataframe": df_atualizado
    }


def menu():
    """
    Interface de terminal CLI autônoma do Membro 2, permitindo testar
    e demonstrar isoladamente cada funcionalidade da Semana 2.
    """
    while True:
        print("\n" + "="*50)
        print("   SCIC - MÓDULO DE MACHINE LEARNING (Semana 2)")
        print("="*50)
        print("1 - Treinar modelo e exibir métricas de performance")
        print("2 - Gerar e salvar gráficos operacionais (Figura 3)")
        print("3 - Atualizar base 'dados_aurora_siger.csv'")
        print("4 - Executar pipeline completo de Machine Learning")
        print("0 - Sair")
        print("="*50)

        opcao = input("Selecione uma opção: ").strip()

        if opcao == "1":
            df = carregar_dados()
            X_train, X_test, y_train, y_test, _, _ = preparar_dados(df)
            mod = treinar_modelo(X_train, y_train)
            pred = mod.predict(X_test)
            m = calcular_metricas(y_test, pred)
            print(interpretar_metricas(m, "Amostra de Teste"))
        elif opcao == "2":
            df = carregar_dados()
            X_train, _, y_train, _, X_full, y_full = preparar_dados(df)
            mod = treinar_modelo(X_train, y_train)
            pred = mod.predict(X_full)
            nomes = df["modulo_nome"].tolist() if "modulo_nome" in df.columns else None
            graficos = gerar_graficos(y_full, pred, nomes)
            print(f"\n✓ Gráficos gerados com sucesso:")
            for g in graficos:
                print(f"  -> {g}")
        elif opcao == "3":
            df = carregar_dados()
            X_train, _, y_train, _, _, _ = preparar_dados(df)
            mod = treinar_modelo(X_train, y_train)
            df_atualizado = atualizar_dataset(mod, df)
            print(f"\n✓ Dataset oficial atualizado:")
            print(df_atualizado[["modulo_nome", "latencia_observada_ms", "latencia_prevista_ms"]])
        elif opcao == "4":
            executar_pipeline_completo()
        elif opcao == "0":
            print("\nEncerrando módulo de Machine Learning. Missão Aurora Siger operando normalmente.")
            break
        else:
            print("\n[!] Opção inválida. Digite um valor entre 0 e 4.")


if __name__ == "__main__":
    # Se chamado com argumento '--pipeline', executa direto sem abrir loop do menu
    if len(sys.argv) > 1 and sys.argv[1] == "--pipeline":
        executar_pipeline_completo()
    else:
        menu()
