import os
import json
import pandas as pd
from .graphs.io import carregar_grafo_recife, tratar_setubal 
from .graphs.graph import Graph
from .graphs.algorithms import dijkstra

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out")

CAMINHO_BAIRROS_UNIQUE = os.path.join(DATA_DIR, "bairros_unique.csv")
CAMINHO_ADJACENCIAS = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

os.makedirs(OUT_DIR, exist_ok=True)

def calcular_metricas_globais(grafo: Graph) -> dict:
    """Calcula ordem, tamanho e densidade do grafo completo."""
    return {
        "ordem": grafo.ordem(),
        "tamanho": grafo.tamanho(),
        "densidade": grafo.densidade()
    }

def calcular_metricas_microrregioes(grafo: Graph, bairro_para_micro: dict):
    """Calcula ordem, tamanho e densidade para cada microrregião."""
    microrregioes = sorted(set(bairro_para_micro.values()))
    resultados = []

    for micro in microrregioes:
        bairros_micro = [b for b, m in bairro_para_micro.items() if m == micro]
        sub = grafo.subgrafo_induzido(bairros_micro)

        resultados.append({
            "microrregiao": micro,
            "ordem": sub.ordem(),
            "tamanho": sub.tamanho(),
            "densidade": sub.densidade()
        })

    return resultados

def calcular_ego_por_bairro(grafo: Graph):
    """Calcula métricas da ego-subrede para cada bairro."""
    linhas = []

    for bairro in grafo.obter_nos():
        vizinhos = [v for (v, _) in grafo.vizinhos(bairro)]
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
    """Gera métricas globais, por microrregião e ego-subrede."""
    grafo, bairro_para_micro = carregar_grafo_recife(
        CAMINHO_BAIRROS_UNIQUE,
        CAMINHO_ADJACENCIAS
    )

    metricas_globais = calcular_metricas_globais(grafo)
    with open(os.path.join(OUT_DIR, "recife_global.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_globais, f, ensure_ascii=False, indent=2)

    metricas_micros = calcular_metricas_microrregioes(grafo, bairro_para_micro)
    with open(os.path.join(OUT_DIR, "microrregioes.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_micros, f, ensure_ascii=False, indent=2)

    ego_linhas = calcular_ego_por_bairro(grafo)
    df_ego = pd.DataFrame(ego_linhas)
    df_ego.to_csv(os.path.join(OUT_DIR, "ego_bairro.csv"), index=False)

def passo_4():
    """Gera rankings de graus e densidades ego."""
    caminho_ego = os.path.join(OUT_DIR, "ego_bairro.csv")
    caminho_graus = os.path.join(OUT_DIR, "graus.csv")
    caminho_densidades = os.path.join(OUT_DIR, "densidades.csv")

    df = pd.read_csv(caminho_ego)

    df_graus = df[["bairro", "grau"]].copy()
    df_graus = df_graus.sort_values(by="grau", ascending=False)
    df_graus.to_csv(caminho_graus, index=False)

    df_den = df[["bairro", "densidade_ego"]].copy()
    df_den = df_den.sort_values(by="densidade_ego", ascending=False)
    df_den.to_csv(caminho_densidades, index=False)

def passo_6():
    """Calcula distâncias entre pares de bairros usando Dijkstra."""
    caminho_enderecos = os.path.join(DATA_DIR, "enderecos.csv")
    caminho_bairros_unique = os.path.join(DATA_DIR, "bairros_unique.csv")
    caminho_adjacencias = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

    caminho_saida_csv = os.path.join(OUT_DIR, "distancias_enderecos.csv")
    caminho_saida_json_nd_setubal = os.path.join(
        OUT_DIR, "percurso_nova_descoberta_setubal.json"
    )

    os.makedirs(OUT_DIR, exist_ok=True)

    grafo, _ = carregar_grafo_recife(
        caminho_bairros_unique,
        caminho_adjacencias
    )

    df_end = pd.read_csv(caminho_enderecos)

    colunas_necessarias = {"bairro_X", "bairro_Y"}
    if not colunas_necessarias.issubset(df_end.columns):
        raise ValueError(
            "O arquivo enderecos.csv deve ter as colunas 'bairro_X' e 'bairro_Y'."
        )

    linhas_saida = []
    info_nd_setubal = None

    for _, linha in df_end.iterrows():
        bairro_X_raw = linha["bairro_X"]
        bairro_Y_raw = linha["bairro_Y"]

        rotulo_X, no_X = tratar_setubal(bairro_X_raw)
        rotulo_Y, no_Y = tratar_setubal(bairro_Y_raw)

        X = rotulo_X
        Y = rotulo_Y

        custo, caminho = dijkstra(grafo, no_X, no_Y)
        caminho_str = " > ".join(caminho) if caminho else ""

        linhas_saida.append({
            "X": X,
            "Y": Y,
            "bairro_X": rotulo_X,
            "bairro_Y": rotulo_Y,
            "custo": custo,
            "caminho": caminho_str
        })
        
        if no_X == "Nova Descoberta" and "Setúbal" in bairro_Y_raw:
            info_nd_setubal = {
                "origem": rotulo_X,
                "destino": rotulo_Y,
                "custo": custo,
                "caminho": caminho
            }

    df_saida = pd.DataFrame(linhas_saida)
    df_saida.to_csv(caminho_saida_csv, index=False)


    if info_nd_setubal is not None:
        with open(caminho_saida_json_nd_setubal, "w", encoding="utf-8") as f:
            json.dump(info_nd_setubal, f, ensure_ascii=False, indent=2)





if __name__ == "__main__":
    passo_3()
    passo_4()
    passo_6()
    
