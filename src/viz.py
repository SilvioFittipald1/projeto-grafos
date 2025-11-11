import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def plot_graph(graph):
    """Funções de visualização para a Parte 1.

    Este módulo gera várias imagens em `out/` usando os arquivos já
    produzidos por `src/solve.py` e `src/graphs/io.py`.
    """
    os.makedirs("out", exist_ok=True)

    # Carrega graus e ego
    graus_path = os.path.join("out", "graus.csv")
    ego_path = os.path.join("out", "ego_bairro.csv")
    bairros_path = os.path.join("data", "bairros_unique.csv")

    if not os.path.exists(graus_path) or not os.path.exists(ego_path) or not os.path.exists(bairros_path):
        print("Arquivos necessários ausentes (graus/ego/bairros_unique). Rode src/solve.py primeiro.")
        return

    df_graus = pd.read_csv(graus_path)
    df_ego = pd.read_csv(ego_path)
    df_bairros = pd.read_csv(bairros_path)

    # monta grafo somente com nós (arestas se existirem serão adicionadas abaixo)
    G = nx.Graph()
    for _, row in df_bairros.iterrows():
        b = row['bairro']
        mic = row.get('microrregiao', '')
        # junta grau/ego se disponível
        grau_row = df_graus[df_graus['bairro'] == b]
        grau = int(grau_row.iloc[0]['grau']) if not grau_row.empty else 0
        ego_row = df_ego[df_ego['bairro'] == b]
        dens_ego = float(ego_row.iloc[0]['densidade_ego']) if not ego_row.empty else 0.0
    G.add_node(b, microrregiao=mic, grau=grau, densidade_ego=dens_ego)

    # tenta carregar adjacencias (se houver) para desenhar arestas
    try:
        from graphs import io as io_mod
        arestas = io_mod.load_adjacencias(os.path.join('data', 'adjacencias_bairros.csv'))
        for o, d, log, obs, peso in arestas:
            G.add_edge(o, d, peso=peso)
    except Exception:
        pass

    # 1) Mapa de cores por grau
    plt.figure(figsize=(12, 9))
    pos = nx.spring_layout(G, seed=42)
    degrees = [G.nodes[n].get('grau', 0) for n in G.nodes()]
    cmap = plt.cm.OrRd
    nx.draw_networkx_nodes(G, pos, node_size=100, node_color=degrees, cmap=cmap)
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.title('Mapa de cores por grau do bairro')
    plt.colorbar(plt.cm.ScalarMappable(cmap=cmap), label='grau')
    fp = os.path.join('out', 'grau_map.png')
    plt.savefig(fp, dpi=150, bbox_inches='tight')
    plt.close()

    # nota analítica
    with open(os.path.join('out', 'insight_grau_map.txt'), 'w', encoding='utf-8') as f:
        f.write('Mapa de cores por grau: bairros com mais interconexoes aparecem com cor mais intensa. Com adjacencias ausentes os valores serão zero.')

    # 2) Ranking de densidade_ego por microrregião (média)
    df = df_bairros.merge(df_ego, on='bairro', how='left')
    df['densidade_ego'] = df['densidade_ego'].fillna(0.0)
    agg = df.groupby('microrregiao')['densidade_ego'].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    agg.plot(kind='bar')
    plt.ylabel('densidade_ego média')
    plt.title('Densidade ego média por microrregião')
    fp = os.path.join('out', 'densidade_ego_microrregiao.png')
    plt.savefig(fp, dpi=150, bbox_inches='tight')
    plt.close()
    with open(os.path.join('out', 'insight_densidade_micros.txt'), 'w', encoding='utf-8') as f:
        f.write('Ranking de densidade_ego por microrregião. Valores próximos de zero indicam pouca conectividade na base atual.')

    # 3) Subgrafo dos 10 bairros com maior grau
    top10 = sorted(G.nodes(data=True), key=lambda x: -x[1].get('grau', 0))[:10]
    sub_nodes = [n for n, _ in top10]
    H = G.subgraph(sub_nodes).copy()
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(H, seed=1)
    nx.draw(H, pos, with_labels=True, node_size=300, node_color='skyblue')
    plt.title('Subgrafo dos 10 bairros com maior grau')
    fp = os.path.join('out', 'subgrafo_top10.png')
    plt.savefig(fp, dpi=150, bbox_inches='tight')
    plt.close()
    with open(os.path.join('out', 'insight_subgrafo_top10.txt'), 'w', encoding='utf-8') as f:
        f.write('Subgrafo dos 10 bairros com maior grau. Se as arestas estiverem ausentes, apenas nós aparecem.')

    # 4) Distribuição dos graus (histograma)
    plt.figure(figsize=(8, 5))
    plt.hist(degrees, bins=range(0, max(degrees) + 2 if degrees else 2), color='gray', edgecolor='black')
    plt.xlabel('Grau')
    plt.ylabel('Número de bairros')
    plt.title('Distribuição dos graus dos bairros')
    fp = os.path.join('out', 'distribuicao_graus.png')
    plt.savefig(fp, dpi=150, bbox_inches='tight')
    plt.close()
    with open(os.path.join('out', 'insight_distribuicao_graus.txt'), 'w', encoding='utf-8') as f:
        f.write('Histograma da distribuição dos graus. Ajuda a ver se há hubs ou distribuição homogênea.')

    # 5) Árvore do percurso (Nova Descoberta -> Boa Viagem (Setúbal))
    percurso_file = os.path.join('out', 'percurso_nova_descoberta_setubal.json')
    if os.path.exists(percurso_file):
        with open(percurso_file, encoding='utf-8') as f:
            p = json.load(f)
        caminho = p.get('caminho') or []
        if caminho and len(caminho) > 1:
            T = nx.Graph()
            nx.add_path(T, caminho)
            plt.figure(figsize=(10, 6))
            pos = nx.spring_layout(T, seed=2)
            nx.draw(T, pos, with_labels=True, node_color='lightgreen', width=2)
            # destaca caminho
            edges_path = list(zip(caminho[:-1], caminho[1:]))
            nx.draw_networkx_edges(T, pos, edgelist=edges_path, width=4, edge_color='red')
            plt.title('Árvore do percurso: Nova Descoberta -> Boa Viagem (Setúbal)')
            fp = os.path.join('out', 'arvore_percurso.png')
            plt.savefig(fp, dpi=150, bbox_inches='tight')
            plt.close()
            with open(os.path.join('out', 'insight_arvore_percurso.txt'), 'w', encoding='utf-8') as f:
                f.write('Árvore construída a partir do percurso armazenado. O caminho principal é destacado em vermelho.')

    print('Visualizações geradas em out/: grau_map, densidade_ego_microrregiao, subgrafo_top10, distribuicao_graus, arvore_percurso (se aplicável).')
