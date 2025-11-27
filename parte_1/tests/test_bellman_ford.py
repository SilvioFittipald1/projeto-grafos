from math import inf
from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src", ROOT_DIR / "parte1" / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists() and str(dir_path) not in sys.path:
        sys.path.append(str(dir_path))

from graphs.graph import Graph
from graphs.algorithms import bellman_ford, bellman_ford_caminho


def montar_grafo_basico() -> Graph:
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 4)
    grafo.adicionar_aresta("A", "C", 2)
    grafo.adicionar_aresta("B", "D", 10)
    grafo.adicionar_aresta("C", "E", 3)
    grafo.adicionar_aresta("E", "D", 4)
    grafo.adicionar_aresta("B", "C", 5)
    return grafo


def reconstruir_caminho(anterior: dict, destino: str):
    caminho = []
    no_atual = destino
    while no_atual is not None:
        caminho.append(no_atual)
        no_atual = anterior[no_atual]
    caminho.reverse()
    return caminho


def test_bellman_ford_retornando_melhores_distancias_e_predecessores():
    grafo = montar_grafo_basico()

    dist, anterior, tem_ciclo = bellman_ford(grafo, "A")

    assert tem_ciclo is False
    assert dist["D"] == pytest.approx(9.0)
    assert reconstruir_caminho(anterior, "D") == ["A", "C", "E", "D"]


def test_bellman_ford_lanca_erro_para_origem_invalida():
    grafo = Graph()
    grafo.adicionar_no("A")

    with pytest.raises(ValueError):
        bellman_ford(grafo, "Inexistente")


def test_bellman_ford_detecta_ciclo_negativo():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_aresta("B", "C", -3)
    grafo.adicionar_aresta("C", "A", 1)

    _dist, _anterior, tem_ciclo = bellman_ford(grafo, "A")

    assert tem_ciclo is True


def test_bellman_ford_caminho_retorna_custo_e_trajeto():
    grafo = montar_grafo_basico()

    custo, caminho, tem_ciclo = bellman_ford_caminho(grafo, "A", "D")

    assert tem_ciclo is False
    assert custo == pytest.approx(9.0)
    assert caminho == ["A", "C", "E", "D"]


def test_bellman_ford_caminho_para_destino_inacessivel():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_no("C")

    custo, caminho, tem_ciclo = bellman_ford_caminho(grafo, "A", "C")

    assert tem_ciclo is False
    assert custo is inf
    assert caminho == []