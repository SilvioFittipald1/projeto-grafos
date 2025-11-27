import os
import json
import pandas as pd
from graphs.io import carregar_grafo_ufc
from graphs.graph import Graph

DATA_DIR = "data"
OUT_DIR = "out/parte2"

CAMINHO_UFC = os.path.join(DATA_DIR, "ufc_arquivo_processado.csv")

os.makedirs(OUT_DIR, exist_ok=True)


def calcular_metricas_globais(grafo: Graph) -> dict:
    """Calcula ordem, tamanho e densidade do grafo de lutadores."""
    return {
        "ordem": grafo.ordem(),
        "tamanho": grafo.tamanho(),
        "densidade": grafo.densidade(),
    }


def gerar_metricas_ufc():
    """Carrega o grafo UFC e gera métricas globais e graus por lutador."""
    grafo = carregar_grafo_ufc(CAMINHO_UFC)

    # métricas globais
    metricas_globais = calcular_metricas_globais(grafo)
    with open(os.path.join(OUT_DIR, "ufc_global.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_globais, f, ensure_ascii=False, indent=2)

    # graus por lutador (para uso em visualizações)
    linhas = []
    for lutador in grafo.obter_nos():
        linhas.append({
            "lutador": lutador,
            "grau": grafo.grau(lutador),
        })

    df_graus = pd.DataFrame(linhas)
    df_graus = df_graus.sort_values(by="grau", ascending=False)
    df_graus.to_csv(os.path.join(OUT_DIR, "graus.csv"), index=False)


if __name__ == "__main__":
    gerar_metricas_ufc()
