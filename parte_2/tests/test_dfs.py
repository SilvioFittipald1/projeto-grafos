from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists():
        sys.path.insert(0, str(dir_path))

from graphs.graph import Graph
from graphs.algorithms import dfs_arvore, dfs_caminho, dfs_detectar_ciclo, dfs_classificar_arestas


def montar_grafo_dfs() -> Graph:
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("A", "C")
    grafo.adicionar_aresta("B", "D")
    grafo.adicionar_aresta("C", "E")
    grafo.adicionar_aresta("E", "F")
    grafo.adicionar_aresta("D", "F")
    return grafo


def test_dfs_arvore_pais_e_ordem_descoberta():
    grafo = montar_grafo_dfs()

    pais, descoberta = dfs_arvore(grafo, "A")

    assert pais["A"] is None
    assert pais["B"] == "A"
    assert pais["C"] == "A"
    assert set(pais.keys()) == {"A", "B", "C", "D", "E", "F"}

    ordem_descoberta = [no for no, _ in sorted(descoberta.items(), key=lambda x: x[1])]
    assert ordem_descoberta[0] == "A"


def test_dfs_arvore_em_grafo_vazio_retorna_apenas_origem():
    grafo = Graph()

    pais, descoberta = dfs_arvore(grafo, "A")

    assert pais == {"A": None}
    assert list(descoberta.keys()) == ["A"]


def test_dfs_caminho_encontra_algum_caminho():
    grafo = montar_grafo_dfs()

    caminho = dfs_caminho(grafo, "A", "F")

    assert caminho[0] == "A"
    assert caminho[-1] == "F"
    assert len(caminho) >= 2


def test_dfs_caminho_origem_igual_destino():
    grafo = montar_grafo_dfs()

    assert dfs_caminho(grafo, "E", "E") == ["E"]


def test_dfs_caminho_para_nos_desconexos():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("C", "D")

    assert dfs_caminho(grafo, "A", "D") == []


def test_dfs_detectar_ciclo_identifica_ciclos_e_florestas():
    grafo_ciclico = Graph()
    grafo_ciclico.adicionar_aresta("A", "B")
    grafo_ciclico.adicionar_aresta("B", "C")
    grafo_ciclico.adicionar_aresta("C", "A")

    grafo_acyclic = Graph()
    grafo_acyclic.adicionar_aresta("X", "Y")
    grafo_acyclic.adicionar_aresta("Y", "Z")

    assert dfs_detectar_ciclo(grafo_ciclico) is True
    assert dfs_detectar_ciclo(grafo_acyclic) is False


def test_dfs_classificar_arestas_tree_e_back():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("B", "C")
    grafo.adicionar_aresta("C", "A")

    classificacao = dfs_classificar_arestas(grafo)

    assert classificacao[tuple(sorted(("A", "B")))] == "tree"
    assert classificacao[tuple(sorted(("B", "C")))] == "tree"
    assert classificacao[tuple(sorted(("A", "C")))] == "back"