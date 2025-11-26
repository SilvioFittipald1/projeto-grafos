import os
import sys
import json
import colorsys
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from typing import Dict, List
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from parte2.io import carregar_grafo_metro, obter_estatisticas_dataset

# Diretório de saída padrão
OUT_DIR = Path(__file__).parent / 'out'


def salvar_distribuicao_graus(grafo, caminho_saida: str = None):
    """
    Gera e salva histograma da distribuição de graus.
    
    Args:
        grafo: Graph
        caminho_saida: caminho para salvar o PNG (padrão: parte2/out/distribuicao_graus.png)
    """
    if caminho_saida is None:
        caminho_saida = str(OUT_DIR / 'distribuicao_graus.png')
    
    nos = grafo.obter_nos()
    graus = [grafo.grau(no) for no in nos]
    
    plt.figure(figsize=(10, 6))
    plt.hist(graus, bins=min(50, max(10, len(set(graus)))), edgecolor='black', alpha=0.7)
    plt.xlabel('Grau do Nó', fontsize=12)
    plt.ylabel('Frequência', fontsize=12)
    plt.title('Distribuição de Graus - Rede Metro RER IDF', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Estatísticas
    grau_medio = np.mean(graus)
    grau_mediano = np.median(graus)
    plt.axvline(grau_medio, color='r', linestyle='--', label=f'Média: {grau_medio:.2f}')
    plt.axvline(grau_mediano, color='g', linestyle='--', label=f'Mediana: {grau_mediano:.2f}')
    plt.legend()
    
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    return caminho_saida


def salvar_estatisticas_dataset(grafo, caminho_saida: str = None):
    """
    Salva estatísticas do dataset em JSON.
    
    Args:
        grafo: Graph
        caminho_saida: caminho para salvar JSON (padrão: parte2/out/estatisticas_dataset.json)
    """
    if caminho_saida is None:
        caminho_saida = str(OUT_DIR / 'estatisticas_dataset.json')
    
    stats = obter_estatisticas_dataset(grafo)
    
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    return caminho_saida, stats


def salvar_lista_graus(grafo, caminho_saida: str = None):
    """
    Salva lista de graus por nó em CSV.
    
    Args:
        grafo: Graph
        caminho_saida: caminho para salvar CSV (padrão: parte2/out/graus.csv)
    """
    if caminho_saida is None:
        caminho_saida = str(OUT_DIR / 'graus.csv')
    
    import pandas as pd
    
    nos = grafo.obter_nos()
    dados = [{'no': no, 'grau': grafo.grau(no)} for no in nos]
    df = pd.DataFrame(dados)
    df = df.sort_values('grau', ascending=False)
    
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    df.to_csv(caminho_saida, index=False)
    
    return caminho_saida


def gerar_arquivos_saida(grafo):
    """
    Gera todos os arquivos de saída úteis em parte2/out/
    
    Args:
        grafo: Graph
    """
    print("\n=== Gerando arquivos de saída em parte2/out/ ===\n")
    
    # Estatísticas do dataset
    print("1. Salvando estatísticas do dataset...")
    caminho_stats, stats = salvar_estatisticas_dataset(grafo)
    print(f"   ✓ {caminho_stats}")
    
    # Distribuição de graus (PNG)
    print("2. Salvando distribuição de graus...")
    caminho_dist = salvar_distribuicao_graus(grafo)
    print(f"   ✓ {caminho_dist}")
    
    # Lista de graus (CSV)
    print("3. Salvando lista de graus...")
    caminho_graus = salvar_lista_graus(grafo)
    print(f"   ✓ {caminho_graus}")
    
    print("\n=== Arquivos de saída gerados ===\n")
    
    return {
        'estatisticas': caminho_stats,
        'distribuicao_graus': caminho_dist,
        'lista_graus': caminho_graus
    }


def app_streamlit():
    """
    Aplicação Streamlit interativa para visualizar o grafo.
    """
    
    st.set_page_config(page_title="Parte 2 - Visualização do Grafo", layout="wide")
    
    st.title("Parte 2: Visualização Interativa do Grafo")
    st.markdown("---")
    
    # Carrega o grafo
    dataset_path = Path(__file__).parent / 'metro_rer_idf.csv'
    
    if not dataset_path.exists():
        st.error(f"Dataset não encontrado: {dataset_path}")
        return
    
    with st.spinner("Carregando grafo..."):
        grafo = carregar_grafo_metro(str(dataset_path), usar_pesos_geograficos=False)
    
    st.success(f"Grafo carregado: {grafo.ordem()} nós, {grafo.tamanho()} arestas")
    
    # Botão para gerar arquivos de saída
    if st.button("Gerar Arquivos de Saída"):
        with st.spinner("Gerando arquivos..."):
            arquivos = gerar_arquivos_saida(grafo)
            st.success("Arquivos gerados em parte2/out/")
            for nome, caminho in arquivos.items():
                st.text(f"{nome}: {Path(caminho).name}")
    
    st.markdown("---")
    
    # Seção 1: Estatísticas do Dataset
    st.header("Estatísticas do Dataset")
    
    stats = obter_estatisticas_dataset(grafo)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ordem (|V|)", stats['ordem'])
    with col2:
        st.metric("Tamanho (|E|)", stats['tamanho'])
    with col3:
        st.metric("Grau Máximo", stats['grau_maximo'])
    
    # Distribuição de graus - gráfico de barras
    st.subheader("Distribuição de Graus")
    nos = grafo.obter_nos()
    graus = [grafo.grau(no) for no in nos]
    
    # Conta quantos nós têm cada grau
    contagem_graus = Counter(graus)
    graus_unicos = sorted(contagem_graus.keys())
    frequencias = [contagem_graus[g] for g in graus_unicos]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(graus_unicos, frequencias, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Grau', fontsize=12)
    ax.set_ylabel('Número de Nós', fontsize=12)
    ax.set_title('Distribuição de Graus - Número de Nós por Grau', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    st.pyplot(fig)
    plt.close()
    
    # Seção 2: Explorar Nós
    st.header("Explorar Nós do Grafo")
    
    no_selecionado = st.selectbox(
        "Selecione um nó para explorar:",
        options=sorted(grafo.obter_nos()),
        index=0
    )
    
    if no_selecionado:
        col1, col2 = st.columns(2)
        
        with col1:
            grau = grafo.grau(no_selecionado)
            st.subheader(f"Grau: {grau}")
            
            vizinhos = grafo.vizinhos(no_selecionado)
            st.subheader(f"**Número de vizinhos:** {len(vizinhos)}")
        
        with col2:
            st.subheader("Vizinhos")
            if vizinhos:
                # Mostra até 20 vizinhos
                for vizinho, peso in vizinhos[:20]:
                    st.write(f"• {vizinho} (peso: {peso:.2f})")
                if len(vizinhos) > 20:
                    st.write(f"... e mais {len(vizinhos) - 20} vizinhos")
            else:
                st.write("Nenhum vizinho")
    
    # Seção 3: Visualização Interativa do Grafo
    st.header("Visualização Interativa do Grafo")
    
    # Carrega informações sobre linhas do dataset
    import pandas as pd
    df_linhas = pd.read_csv(dataset_path)
    
    # Mapeia estação -> linhas (uma estação pode estar em múltiplas linhas)
    estacao_linhas = {}
    for _, row in df_linhas.iterrows():
        estacao = row['station'].strip()
        linha = row['ligne']
        if estacao not in estacao_linhas:
            estacao_linhas[estacao] = []
        if linha not in estacao_linhas[estacao]:
            estacao_linhas[estacao].append(linha)
    
    # Lista de linhas únicas
    linhas_unicas = sorted(set(df_linhas['ligne'].unique()))
    
    # Dropdown para selecionar linha
    linha_selecionada = st.selectbox(
        "Selecione uma linha para destacar:",
        options=["Nenhuma"] + linhas_unicas,
        index=0
    )
    
    with st.spinner("Gerando visualização..."):
        # TODOS os nós e arestas aparecem
        nos_selecionados = set(grafo.obter_nos())
            
        # Cria rede com configurações melhoradas
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#2c3e50",  # Cinza escuro
            font_color="#f8f9fa",  # Texto claro
            directed=False
        )
        
        # Ativa movimento fluido com barnes_hut
        net.barnes_hut()
        
        # Configurações de física para movimento fluido
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "stabilization": {
              "enabled": true,
              "iterations": 200,
              "updateInterval": 25
            },
            "barnesHut": {
              "gravitationalConstant": -2000,
              "centralGravity": 0.1,
              "springLength": 200,
              "springConstant": 0.04,
              "damping": 0.09,
              "avoidOverlap": 0.5
            }
          },
          "nodes": {
            "font": {
              "size": 20,
              "face": "Arial",
              "bold": true,
              "color": "#2c3e50"
            },
            "borderWidth": 0,
            "borderWidthSelected": 0,
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.5)",
              "size": 10,
              "x": 2,
              "y": 2
            }
          },
          "edges": {
            "width": 3,
            "smooth": {
              "type": "continuous",
              "roundness": 0.5
            },
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.3)",
              "size": 5
            }
          }
        }
        """)
            
        # Reconstrói informações de linhas do dataset para mapear arestas
        linhas_estacoes_dict = {}
        for _, row in df_linhas.iterrows():
            linha = row['ligne']
            estacao = row['station'].strip()
            ordem = int(row['ordre'])
            if linha not in linhas_estacoes_dict:
                linhas_estacoes_dict[linha] = []
            linhas_estacoes_dict[linha].append((estacao, ordem))
        
        # Ordena estações por ordem em cada linha
        for linha in linhas_estacoes_dict:
            linhas_estacoes_dict[linha].sort(key=lambda x: x[1])
        
        # Mapeia arestas consecutivas para suas linhas
        aresta_linha = {}  # (u, v) -> lista de linhas
        for linha, estacoes_ordem in linhas_estacoes_dict.items():
            for i in range(len(estacoes_ordem) - 1):
                est1 = estacoes_ordem[i][0]
                est2 = estacoes_ordem[i + 1][0]
                aresta_key = tuple(sorted([est1, est2]))
                if aresta_key not in aresta_linha:
                    aresta_linha[aresta_key] = []
                if linha not in aresta_linha[aresta_key]:
                    aresta_linha[aresta_key].append(linha)
        
        # Identifica nós e arestas da linha selecionada
        nos_linha_selecionada = set()
        arestas_linha_selecionada = set()
        
        if linha_selecionada != "Nenhuma":
            # Encontra todas as estações da linha selecionada
            if linha_selecionada in linhas_estacoes_dict:
                for estacao, _ in linhas_estacoes_dict[linha_selecionada]:
                    nos_linha_selecionada.add(estacao)
            
            # Encontra todas as arestas da linha selecionada
            for aresta_key, linhas in aresta_linha.items():
                if linha_selecionada in linhas:
                    arestas_linha_selecionada.add(aresta_key)
        
        # Adiciona TODOS os nós com cor off-white (sem borda)
        for no in nos_selecionados:
            grau = grafo.grau(no)
            # Tamanho baseado no grau
            if grau >= 8:
                tamanho = 30
            elif grau >= 5:
                tamanho = 25
            elif grau >= 3:
                tamanho = 20
            else:
                tamanho = 15
            
            # Cor off-white por padrão, rosa se for da linha selecionada
            if linha_selecionada != "Nenhuma" and no in nos_linha_selecionada:
                cor_no = "#ff69b4"  # Rosa para nós da linha selecionada
            else:
                cor_no = "#fafafa"  # Off-white para outros nós
            
            net.add_node(
                no,
                label=no,  # Nome completo
                title=f"{no}\nGrau: {grau}\nLinhas: {', '.join(estacao_linhas.get(no, ['N/A']))}",
                color={
                    "background": cor_no,
                    "highlight": {
                        "background": "#fff9c4"
                    }
                },
                size=tamanho,
                font={"size": 18, "face": "Arial", "bold": True, "color": "#2c3e50"}
            )
            
        # Adiciona TODAS as arestas (brancas por padrão, rosa se da linha selecionada)
        arestas_adicionadas = set()
        for u in nos_selecionados:
            for v, peso in grafo.vizinhos(u):
                if v in nos_selecionados:
                    aresta_key = tuple(sorted([u, v]))
                    if aresta_key not in arestas_adicionadas:
                        arestas_adicionadas.add(aresta_key)
                        
                        # Determina cor da aresta: branca por padrão, rosa se da linha selecionada
                        linhas_aresta = aresta_linha.get(aresta_key, [])
                        if linha_selecionada != "Nenhuma" and aresta_key in arestas_linha_selecionada:
                            cor_aresta = "#ff69b4"  # Rosa para arestas da linha selecionada
                            largura = 5  # Mais grossa quando destacada
                        else:
                            cor_aresta = "#ffffff"  # Branca por padrão
                            largura = 2  # Mais fina quando não destacada
                        
                        net.add_edge(
                            u, v,
                            color=cor_aresta,
                            title=f"Peso: {peso:.2f}\nLinha(s): {', '.join(linhas_aresta) if linhas_aresta else 'Correspondência'}",
                            width=largura
                        )
        
        # Salva HTML
        html_path = str(OUT_DIR / f'grafo_interativo_{linha_selecionada.replace(" ", "_")}.html')
        os.makedirs(OUT_DIR, exist_ok=True)
        net.save_graph(html_path)
        
        # Lê o HTML para exibir
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        components.html(html_content, height=800)

        if linha_selecionada != "Nenhuma":
            st.info(f"Linha destacada: {linha_selecionada} (nós e arestas em rosa)")

        st.success(f"Visualização salva em: {html_path}")
    
    # Footer
    st.markdown("---")
    st.caption("Parte 2 - Dataset Maior e Comparação de Algoritmos")


if __name__ == '__main__':
    app_streamlit()
