# src/solve.py
import os
import json
import pandas as pd

from .graphs.io import carregar_grafo_recife, carregar_mapa_bairro_microrregiao
from .graphs.graph import Graph

# Pastas e caminhos padrão
DATA_DIR = "data"
OUT_DIR = "out"

CAMINHO_BAIRROS_UNIQUE = os.path.join(DATA_DIR, "bairros_unique.csv")
CAMINHO_ADJACENCIAS = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

os.makedirs(OUT_DIR, exist_ok=True)


def calcular_metricas_globais(grafo: Graph) -> dict:
    """
    Calcula ordem, tamanho e densidade do grafo completo.
    """
    return {
        "ordem": grafo.ordem(),
        "tamanho": grafo.tamanho(),
        "densidade": grafo.densidade()
    }


def calcular_metricas_microrregioes(grafo: Graph, bairro_para_micro: dict):
    """
    Para cada microrregião, calcula:
        - ordem
        - tamanho
        - densidade
    no subgrafo induzido apenas com seus bairros.
    """
    microrregioes = sorted(set(bairro_para_micro.values()))
    resultados = []

    for micro in microrregioes:
        # bairros dessa microrregião
        bairros_micro = [b for b, m in bairro_para_micro.items() if m == micro]

        # subgrafo induzido
        sub = grafo.subgrafo_induzido(bairros_micro)

        resultados.append({
            "microrregiao": micro,
            "ordem": sub.ordem(),
            "tamanho": sub.tamanho(),
            "densidade": sub.densidade()
        })

    return resultados


def calcular_ego_por_bairro(grafo: Graph):
    """
    Para cada bairro v, considera a ego-subrede v ∪ N(v) e calcula:
        - grau (em G)
        - ordem_ego
        - tamanho_ego
        - densidade_ego
    """
    linhas = []

    for bairro in grafo.obter_nos():
        # vizinhos diretos de v
        vizinhos = [v for (v, _) in grafo.vizinhos(bairro)]

        # nós da ego-subrede: v + vizinhos
        nos_ego = [bairro] + vizinhos

        ego = grafo.subgrafo_induzido(nos_ego)

        linha = {
            "bairro": bairro,
            "grau": grafo.grau(bairro),
            "ordem_ego": ego.ordem(),
            "tamanho_ego": ego.tamanho(),
            "densidade_ego": ego.densidade()
        }
        linhas.append(linha)

    return linhas


def passo_3():
    """
    Orquestra o PASSO 3:

    - Carrega o grafo completo dos bairros (nós + arestas).
    - Calcula métricas globais -> out/recife_global.json
    - Calcula métricas por microrregião -> out/microrregioes.json
    - Calcula ego-subrede por bairro -> out/ego_bairro.csv
    """
    # 1) Carrega grafo completo e mapa bairro -> microrregiao
    grafo, bairro_para_micro = carregar_grafo_recife(
        CAMINHO_BAIRROS_UNIQUE,
        CAMINHO_ADJACENCIAS
    )

    # 2) Métricas globais
    metricas_globais = calcular_metricas_globais(grafo)
    with open(os.path.join(OUT_DIR, "recife_global.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_globais, f, ensure_ascii=False, indent=2)

    # 3) Métricas por microrregião
    metricas_micros = calcular_metricas_microrregioes(grafo, bairro_para_micro)
    with open(os.path.join(OUT_DIR, "microrregioes.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_micros, f, ensure_ascii=False, indent=2)

    # 4) Ego-subrede por bairro
    ego_linhas = calcular_ego_por_bairro(grafo)
    df_ego = pd.DataFrame(ego_linhas)
    df_ego.to_csv(os.path.join(OUT_DIR, "ego_bairro.csv"), index=False)

def passo_4():
    """
    PASSO 4:
    - Lê out/ego_bairro.csv (gerado no passo 3).
    - Gera out/graus.csv com (bairro, grau), ordenado do maior para o menor.
    - Gera out/densidades.csv com (bairro, densidade_ego), ordenado do maior para o menor.
    """
    caminho_ego = os.path.join(OUT_DIR, "ego_bairro.csv")
    caminho_graus = os.path.join(OUT_DIR, "graus.csv")
    caminho_densidades = os.path.join(OUT_DIR, "densidades.csv")

    # Lê a tabela completa de ego-subrede
    df = pd.read_csv(caminho_ego)

    # ----------------- graus.csv -----------------
    df_graus = df[["bairro", "grau"]].copy()
    df_graus = df_graus.sort_values(by="grau", ascending=False)
    df_graus.to_csv(caminho_graus, index=False)

    # --------------- densidades.csv --------------
    df_den = df[["bairro", "densidade_ego"]].copy()
    df_den = df_den.sort_values(by="densidade_ego", ascending=False)
    df_den.to_csv(caminho_densidades, index=False)




if __name__ == "__main__":
    passo_3()
    passo_4()
