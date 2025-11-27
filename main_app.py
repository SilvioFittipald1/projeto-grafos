import os
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARTE1_OUT = os.path.join(BASE_DIR, "parte_1", "out", "parte1")
PARTE2_OUT = os.path.join(BASE_DIR, "parte_2", "out", "parte2")

def listar_htmls(diretorio: str):
    if not os.path.exists(diretorio):
        return []
    return [
        f for f in sorted(os.listdir(diretorio))
        if f.lower().endswith(".html")
    ]

def mostrar_html(caminho_html: str, height: int = 800):
    if not os.path.exists(caminho_html):
        st.warning(f"Arquivo não encontrado: {caminho_html}")
        return
    with open(caminho_html, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=height, scrolling=True)

def pagina_parte1():
    st.header("Parte 1 – Grafos de Recife")
    st.write(
        """Explorações de grafos com dados de bairros de Recife.\n\n"""
    )

    htmls = listar_htmls(PARTE1_OUT)
    if not htmls:
        st.info("Nenhum arquivo HTML encontrado ainda em parte_1/out/parte1.")
        st.code("Rode os scripts da parte_1 para gerar as visualizações.")
        return

    escolha = st.selectbox("Escolha uma visualização da Parte 1:", htmls)
    caminho = os.path.join(PARTE1_OUT, escolha)

    st.subheader(f"Visualização: {escolha}")
    mostrar_html(caminho)


def pagina_parte2():
    st.header("Parte 2 – Grafos do UFC")
    st.write(
        """Visualização interativa do grafo de lutadores do UFC, construída a partir
        do arquivo ufc_arquivo_processado.csv. Cada nó é um lutador e as arestas
        representam lutas realizadas entre eles."""
    )

    htmls = listar_htmls(PARTE2_OUT)
    if not htmls:
        st.info("Nenhum arquivo HTML encontrado ainda em parte_2/out/parte2.")
        st.code("Rode python parte_2/src/viz.py para gerar grafo_interativo.html.")
        return

    # hoje só existe um HTML, mas deixo genérico
    escolha = st.selectbox("Escolha uma visualização da Parte 2:", htmls)
    caminho = os.path.join(PARTE2_OUT, escolha)

    st.subheader(f"Visualização: {escolha}")
    mostrar_html(caminho)


def main():
    st.set_page_config(
        page_title="Projeto Grafos – Navegação",
        layout="wide",
    )

    st.title("Projeto Grafos – Hub de Visualizações")
    st.markdown(
        """\
        Esta interface serve apenas como *ponto de entrada* para as visualizações
        já geradas pelas Partes 1 e 2 do projeto.

        - *Parte 1*: grafos com dados de bairros de Recife (análises diversas).
        - *Parte 2*: grafo interativo de lutadores do UFC.
        """
    )

    aba = st.sidebar.radio(
        "Ir para:",
        ("Parte 1 – Recife", "Parte 2 – UFC"),
    )

    if aba.startswith("Parte 1"):
        pagina_parte1()
    else:
        pagina_parte2()


if __name__ == "__main__":
    main()