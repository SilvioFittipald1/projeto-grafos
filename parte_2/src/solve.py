import os
import json
import pandas as pd
from .graphs.io import carregar_grafo_ufc
from .graphs.graph import Graph

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out")

CAMINHO_UFC = os.path.join(DATA_DIR, "total_fight_data_processado.csv")

os.makedirs(OUT_DIR, exist_ok=True)

def calcular_metricas_globais(grafo: Graph) -> dict:
    return {
        "ordem": grafo.ordem(),
        "tamanho": grafo.tamanho(),
        "densidade": grafo.densidade(),
    }

def gerar_metricas_ufc():
    grafo = carregar_grafo_ufc(CAMINHO_UFC)

    metricas_globais = calcular_metricas_globais(grafo)
    with open(os.path.join(OUT_DIR, "ufc_global.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_globais, f, ensure_ascii=False, indent=2)


def gerar_ranking_vitorias():
    grafo = carregar_grafo_ufc(CAMINHO_UFC)

    todas_vitorias = grafo.obter_todas_vitorias()

    ranking = []
    for lutador, vitorias in todas_vitorias.items():
        ranking.append({
            "lutador": lutador,
            "vitorias": vitorias
        })
 
    ranking_ordenado = sorted(ranking, key=lambda x: x["vitorias"], reverse=True)

    with open(os.path.join(OUT_DIR, "ranking_vitorias.json"), "w", encoding="utf-8") as f:
        json.dump(ranking_ordenado, f, ensure_ascii=False, indent=2)


def gerar_ranking_lutas():
    grafo = carregar_grafo_ufc(CAMINHO_UFC)

    ranking = []
    for lutador in grafo.obter_nos():
        ranking.append({
            "lutador": lutador,
            "numero_lutas": grafo.grau(lutador)
        })

    ranking_ordenado = sorted(ranking, key=lambda x: x["numero_lutas"], reverse=True)

    with open(os.path.join(OUT_DIR, "ranking_lutas.json"), "w", encoding="utf-8") as f:
        json.dump(ranking_ordenado, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    gerar_metricas_ufc()
    gerar_ranking_vitorias()
    gerar_ranking_lutas()
  