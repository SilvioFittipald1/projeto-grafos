# src/solve.py
import os
import json
import pandas as pd
from .graphs.io import carregar_grafo_recife, tratar_setubal 
from .graphs.graph import Graph
from .graphs.algorithms import dijkstra

# Pastas e caminhos padrão
DATA_DIR = "data"
OUT_DIR = "out/parte1"

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

def passo_6():
    """
    PASSO 6:

    - Lê data/enderecos.csv (com bairro_X, bairro_Y).
    - Para cada par, calcula custo e caminho com Dijkstra no grafo de bairros.
    - Gera out/distancias_enderecos.csv com:
        X,Y,bairro_X,bairro_Y,custo,caminho
      (aqui X e Y serão iguais aos bairros, já tratados).
    - Para o par 'Nova Descoberta' -> 'Setúbal', também salva
      out/percurso_nova_descoberta_setubal.json com o caminho.
    """
    DATA_DIR = "data"
    OUT_DIR = "out"

    caminho_enderecos = os.path.join(DATA_DIR, "enderecos.csv")
    caminho_bairros_unique = os.path.join(DATA_DIR, "bairros_unique.csv")
    caminho_adjacencias = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

    caminho_saida_csv = os.path.join(OUT_DIR, "distancias_enderecos.csv")
    caminho_saida_json_nd_setubal = os.path.join(
        OUT_DIR, "percurso_nova_descoberta_setubal.json"
    )

    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) Carrega o grafo completo (nós + arestas)
    grafo, _ = carregar_grafo_recife(
        caminho_bairros_unique,
        caminho_adjacencias
    )

    # 2) Lê o CSV de endereços (no seu caso: bairro_X, bairro_Y)
    df_end = pd.read_csv(caminho_enderecos)

    colunas_necessarias = {"bairro_X", "bairro_Y"}
    if not colunas_necessarias.issubset(df_end.columns):
        raise ValueError(
            "O arquivo enderecos.csv deve ter as colunas 'bairro_X' e 'bairro_Y'."
        )

    linhas_saida = []
    info_nd_setubal = None  # pra guardar o par Nova Descoberta -> Setúbal

    for _, linha in df_end.iterrows():
        bairro_X_raw = linha["bairro_X"]
        bairro_Y_raw = linha["bairro_Y"]

        # Aplica a regra especial de Setúbal + normalização
        # rotulo_* -> vai para os arquivos de saída
        # no_*     -> é o nome do nó no grafo (Boa Viagem, se for Setúbal)
        rotulo_X, no_X = tratar_setubal(bairro_X_raw)
        rotulo_Y, no_Y = tratar_setubal(bairro_Y_raw)

        # X e Y (como o enunciado pede). Aqui iguais aos rótulos dos bairros.
        X = rotulo_X
        Y = rotulo_Y

        # 3) Calcula custo e caminho com Dijkstra
        custo, caminho = dijkstra(grafo, no_X, no_Y)

        # Caminho em formato string para o CSV
        caminho_str = " > ".join(caminho) if caminho else ""

        # Linha para o CSV de distâncias
        linhas_saida.append({
            "X": X,
            "Y": Y,
            "bairro_X": rotulo_X,
            "bairro_Y": rotulo_Y,
            "custo": custo,
            "caminho": caminho_str
        })

       
    # 4) Salva o CSV de distâncias
    df_saida = pd.DataFrame(linhas_saida)
    df_saida.to_csv(caminho_saida_csv, index=False)

    # 5) Salva o JSON do percurso Nova Descoberta -> Setúbal, se existir
    if info_nd_setubal is not None:
        with open(caminho_saida_json_nd_setubal, "w", encoding="utf-8") as f:
            json.dump(info_nd_setubal, f, ensure_ascii=False, indent=2)





if __name__ == "__main__":
    passo_3()
    passo_4()
    passo_6()
