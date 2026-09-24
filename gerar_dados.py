"""
Script de Geração da Base de Dados de Telemetria - Missão Aurora Siger (SCIC Fase 6)
Gera dados simulados realistas de comunicação, grandezas elétricas (Tensão, Corrente)
e ciclos operacionais da colônia para permitir o treinamento de Machine Learning e análises numéricas.
"""

import numpy as np
import pandas as pd

def gerar_dataset_colonia(caminho_saida: str = "dados_aurora_siger.csv", random_seed: int = 42):
    """
    Gera uma base consistente com 80 registros cobrindo 10 ciclos operacionais
    de 8 módulos da colônia marciana Aurora Siger.
    """
    np.random.seed(random_seed)

    modulos_colonia = [
        # (nome, tipo, prefixo_hex, tensao_nominal, corrente_nominal, prioridade, latencia_base)
        ("Suporte Vital", "suporte_medico", "0xA1", 12.0, 3.8, 1, 48.5),
        ("Energia", "armazenamento_dados", "0xB2", 24.0, 8.5, 2, 55.2),
        ("Comunicacao", "comunicacao", "0xC3", 5.0, 1.2, 3, 43.0),
        ("Habitat", "habitacao", "0xD4", 12.0, 2.5, 4, 62.1),
        ("Laboratorio", "laboratorio", "0xE5", 9.0, 2.0, 5, 44.8),
        ("Agricultura", "agricultura", "0xF1", 15.0, 4.2, 2, 52.3),
        ("Controle Termico", "habitacao", "0x88", 18.0, 5.0, 3, 56.4),
        ("Estacao Externa", "comunicacao", "0x99", 6.0, 1.5, 1, 44.1)
    ]

    registros = []

    # Ciclo 1: Preserva exatamente os 5 registros históricos originais da colônia
    registros_ciclo_1 = {
        "Suporte Vital": {"tipo": "suporte_medico", "hex": "0xA1F3", "lat": 48.5, "v": 12.0, "i": 3.8, "status": "ativo", "prio": 1},
        "Energia":       {"tipo": "armazenamento_dados", "hex": "0xB2C4", "lat": 55.2, "v": 24.0, "i": 8.5, "status": "alerta", "prio": 2},
        "Comunicacao":   {"tipo": "comunicacao", "hex": "0xC3D5", "lat": 43.0, "v": 5.0,  "i": 1.2, "status": "ativo", "prio": 3},
        "Habitat":       {"tipo": "habitacao", "hex": "0xD4E6", "lat": 62.1, "v": 12.0, "i": 2.5, "status": "manutencao", "prio": 4},
        "Laboratorio":   {"tipo": "laboratorio", "hex": "0xE5F7", "lat": 44.8, "v": 9.0,  "i": 2.0, "status": "ativo", "prio": 5},
    }

    for nome, dados in registros_ciclo_1.items():
        registros.append({
            "modulo_nome": nome,
            "modulo_tipo": dados["tipo"],
            "sensor_hex_id": dados["hex"],
            "latencia_observada_ms": dados["lat"],
            "tensao_v": dados["v"],
            "corrente_a": dados["i"],
            "status": dados["status"],
            "prioridade": dados["prio"],
            "ciclo": 1
        })

    # Adiciona os módulos restantes no Ciclo 1 para consistência de telemetria
    for nome, tipo, prefix, base_v, base_i, prio, base_lat in modulos_colonia:
        if nome in registros_ciclo_1:
            continue
        registros.append({
            "modulo_nome": nome,
            "modulo_tipo": tipo,
            "sensor_hex_id": f"{prefix}01",
            "latencia_observada_ms": base_lat,
            "tensao_v": base_v,
            "corrente_a": base_i,
            "status": "ativo",
            "prioridade": prio,
            "ciclo": 1
        })

    # Ciclos 2 a 10: Variações operacionais e elétricas realistas da colônia
    for ciclo in range(2, 11):
        for nome, tipo, prefix, base_v, base_i, prio, base_lat in modulos_colonia:
            # Oscilação física de tensão e corrente nos circuitos marcianos (+- 3 a 5%)
            v = round(base_v + np.random.normal(0, base_v * 0.035), 2)
            i = round(base_i + np.random.normal(0, base_i * 0.045), 2)
            v = max(v, 1.0)
            i = max(i, 0.2)

            # Relação física da latência com tensão, corrente e ruído de transmissão
            # Variação proporcional ao comportamento dos transmissores da colônia
            delta_v = v - base_v
            delta_i = i - base_i
            ruido = np.random.normal(0, 0.75)
            
            # Cálculo de latência observada coerente com a física de propagação
            lat = round(base_lat + (0.75 * delta_v) + (1.20 * delta_i) + ruido, 2)

            # ID Hexadecimal do sensor para cada ciclo (compatível com bases numéricas e Trie)
            hex_id = f"{prefix}{ciclo:02X}"

            # Regra de status operacional baseado no limiar de latência
            if lat >= 60.0:
                status = "manutencao" if lat >= 63.0 else "alerta"
            elif lat >= 53.0 and np.random.rand() > 0.65:
                status = "alerta"
            else:
                status = "ativo"

            registros.append({
                "modulo_nome": nome,
                "modulo_tipo": tipo,
                "sensor_hex_id": hex_id,
                "latencia_observada_ms": lat,
                "tensao_v": v,
                "corrente_a": i,
                "status": status,
                "prioridade": prio,
                "ciclo": ciclo
            })

    df = pd.DataFrame(registros)
    df.to_csv(caminho_saida, index=False, encoding="utf-8")
    print(f"✓ Base '{caminho_saida}' gerada com sucesso: {len(df)} registros ao longo de 10 ciclos.")
    return df

if __name__ == "__main__":
    gerar_dataset_colonia()
