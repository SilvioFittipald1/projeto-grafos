from pathlib import Path
import sys

import pytest
from math import isinf

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src", ROOT_DIR / "parte1" / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists() and str(dir_path) not in sys.path:
        sys.path.append(str(dir_path))

from graphs.graph import Graph
from graphs.algorithms import dijkstra


def montar_grafo_dijkstra() -> Graph:
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_aresta("A", "C", 4)
    grafo.adicionar_aresta("B", "C", 2)
    grafo.adicionar_aresta("B", "D", 6)
    grafo.adicionar_aresta("C", "D", 3)
    grafo.adicionar_aresta("C", "E", 2)
    grafo.adicionar_aresta("D", "E", 1)
    return grafo


def test_dijkstra_retorna_menor_caminho_e_custo():
    grafo = montar_grafo_dijkstra()

    custo, caminho = dijkstra(grafo, "A", "E")

    assert custo == pytest.approx(5.0)
    assert caminho == ["A", "B", "C", "E"]


def test_dijkstra_retorna_inf_para_destino_fora_do_grafo():
    grafo = montar_grafo_dijkstra()

    custo, caminho = dijkstra(grafo, "A", "Z")

    assert isinf(custo)
    assert caminho == []


def test_dijkstra_retorna_inf_para_origem_fora_do_grafo():
    grafo = montar_grafo_dijkstra()

    custo, caminho = dijkstra(grafo, "Z", "A")

    assert isinf(custo)
    assert caminho == []


def test_dijkstra_destino_inacessivel():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_no("C")

    custo, caminho = dijkstra(grafo, "A", "C")

    assert custo == float("inf")
    assert caminho == []


def test_dijkstra_para_origem_igual_destino():
    grafo = montar_grafo_dijkstra()

    custo, caminho = dijkstra(grafo, "B", "B")

    assert custo == pytest.approx(0.0)
    assert caminho == ["B"]


def test_dijkstra_recusa_pesos_negativos():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", -1)

    with pytest.raises(ValueError):
        dijkstra(grafo, "A", "B")