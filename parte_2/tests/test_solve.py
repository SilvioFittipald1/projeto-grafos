from pathlib import Path
import sys

import json

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists():
        sys.path.insert(0, str(dir_path))

from graphs.graph import Graph
import solve


def criar_grafo_para_metricas() -> Graph:
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1.0)
    grafo.adicionar_aresta("A", "C", 2.0)
    return grafo


def test_calcular_metricas_globais_retorna_ordem_tamanho_e_densidade():
    grafo = criar_grafo_para_metricas()

    metricas = solve.calcular_metricas_globais(grafo)

    assert metricas["ordem"] == grafo.ordem()
    assert metricas["tamanho"] == grafo.tamanho()
    assert metricas["densidade"] == pytest.approx(grafo.densidade())


def test_gerar_metricas_ufc_cria_arquivo_json(tmp_path, monkeypatch):
    grafo = criar_grafo_para_metricas()

    def carregar_mock(_):
        return grafo

    monkeypatch.setattr(solve, "carregar_grafo_ufc", carregar_mock)
    monkeypatch.setattr(solve, "OUT_DIR", str(tmp_path))
    monkeypatch.setattr(solve, "CAMINHO_UFC", str(tmp_path / "nao_importa.csv"))

    solve.gerar_metricas_ufc()

    caminho_json = tmp_path / "ufc_global.json"
    assert caminho_json.exists()

    dados = json.loads(caminho_json.read_text(encoding="utf-8"))
    assert dados["ordem"] == grafo.ordem()
    assert dados["tamanho"] == grafo.tamanho()


def test_gerar_ranking_vitorias_usa_dados_de_vitorias(tmp_path, monkeypatch):
    grafo = Graph()
    grafo.adicionar_no("A")
    grafo.adicionar_no("B")
    grafo.adicionar_no("C")
    grafo.registrar_vitoria("A")
    grafo.registrar_vitoria("A")
    grafo.registrar_vitoria("B")

    def carregar_mock(_):
        return grafo

    monkeypatch.setattr(solve, "carregar_grafo_ufc", carregar_mock)
    monkeypatch.setattr(solve, "OUT_DIR", str(tmp_path))

    solve.gerar_ranking_vitorias()

    caminho_json = tmp_path / "ranking_vitorias.json"
    assert caminho_json.exists()

    ranking = json.loads(caminho_json.read_text(encoding="utf-8"))
    assert ranking[0]["lutador"] == "A"
    assert ranking[0]["vitorias"] == 2
    assert ranking[1]["lutador"] == "B"
    assert ranking[1]["vitorias"] == 1


def test_gerar_ranking_lutas_usa_grau_do_grafo(tmp_path, monkeypatch):
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("A", "C")

    def carregar_mock(_):
        return grafo

    monkeypatch.setattr(solve, "carregar_grafo_ufc", carregar_mock)
    monkeypatch.setattr(solve, "OUT_DIR", str(tmp_path))

    solve.gerar_ranking_lutas()

    caminho_json = tmp_path / "ranking_lutas.json"
    assert caminho_json.exists()

    ranking = json.loads(caminho_json.read_text(encoding="utf-8"))
    assert ranking[0]["lutador"] == "A"
    assert ranking[0]["numero_lutas"] == 2


def test_gerar_descricao_dataset_usa_metricas_do_grafo(tmp_path, monkeypatch):
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("A", "C")
    grafo.adicionar_aresta("B", "C")

    def carregar_mock(_):
        return grafo

    monkeypatch.setattr(solve, "carregar_grafo_ufc", carregar_mock)
    monkeypatch.setattr(solve, "OUT_DIR", str(tmp_path))

    solve.gerar_descricao_dataset()

    caminho_txt = tmp_path / "descricao_dataset.txt"
    assert caminho_txt.exists()

    conteudo = caminho_txt.read_text(encoding="utf-8")
    assert str(grafo.ordem()) in conteudo
    assert str(grafo.tamanho()) in conteudo
