from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists():
        sys.path.insert(0, str(dir_path))

from graphs.graph import Graph


def criar_grafo_basico() -> Graph:
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1.5)
    grafo.adicionar_aresta("A", "C", 2.0)
    grafo.adicionar_aresta("B", "C", 3.0)
    grafo.adicionar_no("Isolado")
    return grafo


def test_adicionar_no_e_aresta_gera_grafo_nao_direcionado():
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1.0)

    assert "A" in grafo.adjacencia
    assert "B" in grafo.adjacencia
    assert ("B", 1.0) in grafo.vizinhos("A")
    assert ("A", 1.0) in grafo.vizinhos("B")


def test_ordem_tamanho_grau_e_densidade():
    grafo = criar_grafo_basico()

    assert grafo.ordem() == 4
    assert grafo.tamanho() == 3
    assert grafo.grau("A") == 2
    assert grafo.grau("Isolado") == 0

    densidade_esperada = (2 * grafo.tamanho()) / (grafo.ordem() * (grafo.ordem() - 1))
    assert grafo.densidade() == pytest.approx(densidade_esperada)


def test_registrar_vitorias_e_obter_vitorias():
    grafo = Graph()
    grafo.adicionar_no("Lutador1")

    assert grafo.obter_vitorias("Lutador1") == 0

    grafo.registrar_vitoria("Lutador1")
    grafo.registrar_vitoria("Lutador1")
    grafo.registrar_vitoria("Lutador2")

    assert grafo.obter_vitorias("Lutador1") == 2
    assert grafo.obter_vitorias("Lutador2") == 1

    vitorias = grafo.obter_todas_vitorias()
    assert vitorias["Lutador1"] == 2
    assert vitorias["Lutador2"] == 1

    vitorias["Lutador1"] = 999
    assert grafo.obter_vitorias("Lutador1") == 2


def test_subgrafo_induzido_mantem_apenas_lutadores_e_arestas_do_conjunto():
    grafo = criar_grafo_basico()

    sub = grafo.subgrafo_induzido(["A", "B", "Isolado"])

    assert set(sub.obter_nos()) == {"A", "B", "Isolado"}
    assert sub.grau("A") == 1
    assert sub.grau("B") == 1
    assert sub.grau("Isolado") == 0
    assert sub.tamanho() == 1
