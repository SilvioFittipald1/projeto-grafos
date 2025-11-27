from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists():
        sys.path.insert(0, str(dir_path))

from graphs.graph import Graph
import viz


class NetworkStub:
    def __init__(self, *_, **__):
        self.nodes = []
        self.edges = []

    def barnes_hut(self):
        pass

    def set_options(self, *_args, **_kwargs):
        pass

    def add_node(self, *args, **kwargs):
        self.nodes.append((args, kwargs))

    def add_edge(self, *args, **kwargs):
        self.edges.append((args, kwargs))

    def show(self, path, notebook=False):
        with open(path, "w", encoding="utf-8") as f:
            f.write("<html><body>Grafo</body></html>")


def criar_grafo_simples() -> Graph:
    grafo = Graph()
    grafo.adicionar_aresta("A", "B", 1.0)
    grafo.registrar_vitoria("A")
    return grafo


def test_grafo_interativo_ufc_html_gera_arquivo_html(tmp_path, monkeypatch):
    grafo = criar_grafo_simples()

    def carregar_mock(_):
        return grafo

    monkeypatch.setattr(viz, "carregar_grafo_ufc", carregar_mock)
    monkeypatch.setattr(viz, "OUT_DIR", str(tmp_path))
    monkeypatch.setattr(viz, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(viz, "Network", NetworkStub)

    viz.grafo_interativo_ufc_html()

    caminho_html = tmp_path / "grafo_interativo.html"
    assert caminho_html.exists()
    conteudo = caminho_html.read_text(encoding="utf-8")
    assert "html" in conteudo.lower()


def test_gerar_histograma_graus_cria_csv_e_png(tmp_path, monkeypatch):
    grafo = Graph()
    grafo.adicionar_aresta("A", "B")
    grafo.adicionar_aresta("B", "C")

    def carregar_mock(_):
        return grafo

    monkeypatch.setattr(viz, "carregar_grafo_ufc", carregar_mock)
    monkeypatch.setattr(viz, "OUT_DIR", str(tmp_path))
    monkeypatch.setattr(viz, "DATA_DIR", str(tmp_path))

    viz.gerar_histograma_graus()

    assert (tmp_path / "graus_lutadores.csv").exists()
    assert (tmp_path / "distribuicao_graus.png").exists()
