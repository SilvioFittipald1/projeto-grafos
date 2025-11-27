from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists():
        sys.path.insert(0, str(dir_path))

from graphs.graph import Graph
from graphs.algorithms import bfs_arvore, bfs_caminho


def montar_grafo_bfs() -> Graph:
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("A", "C")
    grafo.adicionar_aresta("B", "D")
    grafo.adicionar_aresta("B", "E")
    grafo.adicionar_aresta("C", "F")
    grafo.adicionar_aresta("E", "F")
    grafo.adicionar_aresta("E", "G")
    return grafo


def test_bfs_arvore_retorna_pais_e_niveis():
    grafo = montar_grafo_bfs()

    pais, niveis = bfs_arvore(grafo, "A")

    assert pais == {"A": None, "B": "A", "C": "A", "D": "B", "E": "B", "F": "C", "G": "E"}
    assert niveis == {"A": 0, "B": 1, "C": 1, "D": 2, "E": 2, "F": 2, "G": 3}


def test_bfs_arvore_em_grafo_vazio_retorna_apenas_origem():
    grafo = Graph()

    pais, niveis = bfs_arvore(grafo, "A")

    assert pais == {"A": None}
    assert niveis == {"A": 0}


def test_bfs_caminho_menor_numero_arestas():
    grafo = montar_grafo_bfs()

    caminho = bfs_caminho(grafo, "A", "G")

    assert caminho == ["A", "B", "E", "G"]


def test_bfs_caminho_origem_igual_destino():
    grafo = montar_grafo_bfs()

    assert bfs_caminho(grafo, "C", "C") == ["C"]


def test_bfs_caminho_inexistente():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("C", "D")

    caminho = bfs_caminho(grafo, "A", "D")

    assert caminho == []