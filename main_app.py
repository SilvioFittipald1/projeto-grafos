import os
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARTE1_OUT = os.path.join(BASE_DIR, "parte_1", "out")
PARTE2_OUT = os.path.join(BASE_DIR, "parte_2", "out")

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
        """Exploração de outpus gerados com dados de bairros do Recife.\n\n"""
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
    st.header("Parte 2 – Grafo de Network dos Lutadores do UFC")
    st.write(
        """Visualizações interativas do grafo de lutadores do UFC, construídas a partir
        do arquivo raw_total_fight_data.csv. Cada nó é um lutador e as arestas
        representam lutas realizadas entre eles."""
    )

    htmls = listar_htmls(PARTE2_OUT)
    if not htmls:
        st.info("Nenhum arquivo HTML encontrado ainda em parte_2/out.")
        st.code("Rode os scripts da parte_2 para gerar as visualizações.")
        return

    escolha = st.selectbox("Escolha uma visualização da Parte 2:", htmls)
    caminho = os.path.join(PARTE2_OUT, escolha)

    st.subheader(f"Visualização: {escolha}")
    mostrar_html(caminho)


def main():
    st.set_page_config(
        page_title="Projeto Grafos",
        layout="wide",
    )
    
    # Aplicar paleta de cores customizada apenas na sidebar
    st.markdown("""
        <style>
        /* Sidebar com paleta similar ao viz.py */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #16213e 0%, #1a1a2e 100%);
        }
        
        /* Títulos e textos da sidebar */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }
        
        /* Botões de rádio na sidebar */
        [data-testid="stSidebar"] .stRadio > label {
            color: #4fc3f7 !important;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: rgba(255,255,255,0.05);
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 8px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }
        
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(79, 195, 247, 0.15);
            border-color: #4fc3f7;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Hub de Visualizações do Projeto de Teoria dos Grafos")

    aba = st.sidebar.radio(
        "Navegação:",
        ("Parte 1", "Parte 2"),
    )

    if aba.startswith("Parte 1"):
        pagina_parte1()
    else:
        pagina_parte2()


if __name__ == "__main__":
    main()