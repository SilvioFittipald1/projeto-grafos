# src/viz.py

import os
import json
import pandas as pd
from pyvis.network import Network
from graphs.io import carregar_grafo_recife
from graphs.algorithms import bfs_arvore, dijkstra
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

OUT_DIR = "out/parte1"


def percurso_nova_descoberta_setubal(caminho_json: str | None = None):
    """
    Lê o arquivo JSON gerado no PASSO 6 (percurso Nova Descoberta -> Setúbal)
    e devolve (origem, destino_rotulo, caminho).

    - origem: string (ex.: "Nova Descoberta")
    - destino_rotulo: string para exibição (ex.: "Boa Viagem (Setúbal)")
    - caminho: lista de bairros (como usados no grafo, ex.: ["Nova Descoberta", ..., "Boa Viagem"])
    """
    if caminho_json is None:
        caminho_json = os.path.join(OUT_DIR, "percurso_nova_descoberta_setubal.json")

    if not os.path.exists(caminho_json):
        raise FileNotFoundError(
            f"Arquivo de percurso não encontrado: {caminho_json}. "
            f"Certifique-se de rodar o PASSO 6 antes."
        )

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    origem = dados.get("origem")
    destino_rotulo = dados.get("destino")  # ex.: "Boa Viagem (Setúbal)"
    caminho = dados.get("caminho", [])     # lista de bairros (nós do grafo)

    if not caminho:
        raise ValueError(
            f"O arquivo {caminho_json} não contém um caminho válido (lista vazia)."
        )

    return origem, destino_rotulo, caminho


def arvore_percurso_html(
    caminho_json: str | None = None,
    caminho_saida: str | None = None
):
    """
    Gera uma visualização INTERATIVA da árvore de percurso
    (Nova Descoberta -> Boa Viagem (Setúbal)) usando pyvis.

    Salva o resultado em out/parte1/arvore_percurso.html.
    """

    # carrega o caminho do arquivo json que tem o percurso
    origem, destino_rotulo, caminho = percurso_nova_descoberta_setubal(
        caminho_json
    )

    if caminho_saida is None:
        caminho_saida = os.path.join("out/parte1", "arvore_percurso.html")

    os.makedirs(OUT_DIR, exist_ok=True)

    # prepara os nomes que vão aparecer nos nós
    labels = list(caminho)
    if destino_rotulo and len(labels) > 0:
        labels[-1] = destino_rotulo  # exibe "Boa Viagem (Setúbal)" no último nó

    # configura o tamanho da fonte e dos nós
    NODE_SIZE = 14
    FONT = {"size": 14, "face": "Arial", "strokeWidth": 0}

    # cria a rede e usa o algoritmo de barnes hut pra ficar mais rápido
    net = Network(height="600px", width="100%", directed=False)
    net.barnes_hut()

    # ajusta as opções de visualização
    net.set_options('''{
      "nodes": { "font": { "size": 14, "face": "Arial" } },
      "edges": { "smooth": false },
      "physics": { "stabilization": { "enabled": true, "iterations": 800 } }
    }''')

    # adiciona cada ponto do caminho, destacando o começo e o fim
    for i, label in enumerate(labels):
        titulo = label
        if i == 0:
            # pinta o ponto de partida de rosa
            color = {"background": "#ff66c4", "border": "#c0428f"}
        elif i == len(labels) - 1:
            # pinta o ponto de chegada de rosa também
            color = {"background": "#ff66c4", "border": "#c0428f"}
        else:
            # os pontos do meio ficam azuis
            color = {"background": "#8ecae6", "border": "#2b7f9e"}

        net.add_node(label, label=label, title=titulo, color=color, size=NODE_SIZE, font=FONT)

    # liga os pontos com linhas
    for i in range(len(labels) - 1):
        u = labels[i]
        v = labels[i + 1]
        net.add_edge(u, v, color="#dcdcdc", width=2)

    # salva o arquivo html com o grafo
    net.show(caminho_saida, notebook=False)

def cor_por_grau(grau: int, gmin: int, gmax: int) -> str:
    """
    Converte o grau de um bairro em uma cor (hex) mais ou menos intensa.

    Usamos um gradiente de azul claro -> azul escuro.
    """
    if gmax <= gmin:
        t = 0.5
    else:
        t = (grau - gmin) / (gmax - gmin)  # normaliza para [0, 1]

    # Azul claro -> azul escuro
    r1, g1, b1 = (198, 219, 239)
    r2, g2, b2 = (8, 48, 107)

    r = int(r1 + t * (r2 - r1))
    g = int(g1 + t * (g2 - g1))
    b = int(b1 + t * (b2 - b1))

    return f"#{r:02x}{g:02x}{b:02x}"



DATA_DIR = "data/"
OUT_DIR = "out/parte1"


def _controles_zoom_navegacao():
    """
    Retorna HTML e JavaScript para controles de zoom e navegação reutilizáveis.
    """
    return """
<style>
  .zoom-controls {
    position: fixed;
    left: 120px;
    bottom: 80px;
    z-index: 9999;
    background: rgba(255,255,255,0.95);
    padding: 8px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    display: flex;
    gap: 4px;
  }
  .zoom-controls button {
    background: #f0f0f0;
    border: 1px solid #ccc;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    transition: background 0.2s;
  }
  .zoom-controls button:hover {
    background: #e0e0e0;
  }
  .zoom-controls button:active {
    background: #d0d0d0;
  }
  .navigation-controls {
    position: fixed;
    right: 120px;
    bottom: 80px;
    z-index: 9999;
    background: rgba(255,255,255,0.95);
    padding: 8px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }
  .nav-row {
    display: flex;
    gap: 2px;
    justify-content: center;
  }
  .nav-btn {
    background: #f0f0f0;
    border: 1px solid #ccc;
    padding: 6px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
  }
  .nav-btn:hover {
    background: #e0e0e0;
  }
  .nav-btn:active {
    background: #d0d0d0;
  }
  .nav-btn.center {
    font-size: 12px;
  }
</style>
<div class="zoom-controls">
  <button onclick="zoomIn()">+</button>
  <button onclick="zoomOut()">-</button>
  <button onclick="resetZoom()">Reset</button>
</div>
<div class="navigation-controls">
  <div class="nav-row">
    <button onclick="moveView('up')" class="nav-btn">⬆️</button>
  </div>
  <div class="nav-row">
    <button onclick="moveView('left')" class="nav-btn">⬅️</button>
    <button onclick="moveView('center')" class="nav-btn center"></button>
    <button onclick="moveView('right')" class="nav-btn">➡️</button>
  </div>
  <div class="nav-row">
    <button onclick="moveView('down')" class="nav-btn">⬇️</button>
  </div>
</div>
<script>
function zoomIn() {
    var scale = network.getScale();
    network.moveTo({
        scale: Math.min(scale * 1.3, 5),
        animation: { duration: 300 }
    });
}
function zoomOut() {
    var scale = network.getScale();
    network.moveTo({
        scale: Math.max(scale / 1.3, 0.1),
        animation: { duration: 300 }
    });
}
function resetZoom() {
    network.fit({
        animation: { duration: 600, easingFunction: 'easeInOutQuad' }
    });
}
function moveView(direction) {
    var moveAmount = 100;
    var position = network.getViewPosition();
    var scale = network.getScale();
    
    if (!position) {
        position = { x: 0, y: 0 };
    }
    
    var newPosition = { x: position.x, y: position.y };
    
    switch(direction) {
        case 'up':
            newPosition.y -= moveAmount;
            break;
        case 'down':
            newPosition.y += moveAmount;
            break;
        case 'left':
            newPosition.x -= moveAmount;
            break;
        case 'right':
            newPosition.x += moveAmount;
            break;
        case 'center':
            network.fit({
                animation: { duration: 400, easingFunction: 'easeInOutQuad' }
            });
            return;
    }
    
    network.moveTo({
        position: newPosition,
        scale: scale,
        animation: { duration: 300, easingFunction: 'easeInOutQuad' }
    });
}
</script>
"""


def mapa_graus_html():
    """
    Gera um HTML interativo (pyvis) onde:
    - cada nó é um bairro
    - a cor do nó varia com o grau (mais conexões = cor mais intensa)

    Usa o arquivo out/parte1/graus.csv já gerado no passo 4.

    Saída: out/parte1/mapa_graus.html
    """
    if Network is None:
        print("Pyvis não está disponível (Network é None). Verifique pyvis/jinja2 no ambiente.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    caminho_bairros_unique = os.path.join(DATA_DIR, "bairros_unique.csv")
    caminho_adjacencias = os.path.join(DATA_DIR, "adjacencias_bairros.csv")
    caminho_graus = os.path.join(OUT_DIR, "graus.csv")

    # 1) Carrega o grafo (para ter as arestas)
    grafo, _ = carregar_grafo_recife(
        caminho_bairros_unique,
        caminho_adjacencias
    )

    # 2) Lê o CSV de graus já calculado
    if not os.path.exists(caminho_graus):
        raise FileNotFoundError(
            f"Arquivo de graus não encontrado: {caminho_graus}. "
            f"Certifique-se de rodar o passo 4 antes."
        )

    df_graus = pd.read_csv(caminho_graus)
    df_graus.columns = df_graus.columns.str.strip().str.lower()

    if not {"bairro", "grau"}.issubset(df_graus.columns):
        raise ValueError("O arquivo graus.csv deve ter as colunas 'bairro' e 'grau'.")

    # Mapeia bairro -> grau
    graus = {row["bairro"]: int(row["grau"]) for _, row in df_graus.iterrows()}

    # Podemos pegar os bairros diretamente do CSV de graus
    bairros = list(graus.keys())

    gmin = min(graus.values())
    gmax = max(graus.values())

    # 3) Cria a rede pyvis (usar tamanhos e fontes consistentes com o grafo interativo)
    NODE_SIZE = 14
    FONT = {"size": 14, "face": "Arial", "strokeWidth": 0}

    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000"
    )
    net.barnes_hut()

    # aplica opções de vis.js para uniformidade e legibilidade
    net.set_options('''{
        "nodes": { "font": { "size": 14, "face": "Arial" } },
        "edges": { "smooth": false },
        "physics": { "stabilization": { "enabled": true, "iterations": 1000 } }
    }''')

    # usa um colormap tipo 'YlOrRd' para representar calor (mais conexoes = mais quente)
    try:
        cmap = plt.get_cmap('YlOrRd')
        norm = matplotlib.colors.Normalize(vmin=gmin, vmax=gmax)
        def map_color(v):
            return matplotlib.colors.to_hex(cmap(norm(v)))
    except Exception:
        # fallback para a paleta antiga
        def map_color(v):
            return cor_por_grau(v, gmin, gmax)

    # 4) Adiciona nós com cor baseada no grau (heatmap) e tamanho uniforme
    for bairro in bairros:
        grau = graus[bairro]
        cor = map_color(grau)
        title = f"{bairro}<br>Grau: {grau}"

        net.add_node(
            bairro,
            label=bairro,
            title=title,
            color={"background": cor, "border": "#222222"},
            size=NODE_SIZE,
            font=FONT
        )

    # 5) Adiciona arestas (sem duplicar, grafo não dirigido) com largura uniforme
    arestas_adicionadas = set()
    for b in bairros:
        for vizinho, peso in grafo.vizinhos(b):
            if vizinho not in graus:
                continue
            aresta = tuple(sorted((b, vizinho)))
            if aresta in arestas_adicionadas:
                continue
            net.add_edge(b, vizinho, color="#dcdcdc", width=2)
            arestas_adicionadas.add(aresta)

    # 6) Salva o HTML
    caminho_saida = os.path.join("out/parte1", "mapa_graus.html")
    net.show(caminho_saida, notebook=False)  # notebook=False para evitar o bug do template
    print(caminho_saida)

    # 7) Pos-processa HTML para adicionar uma legenda de cores (heatmap) no canto superior direito
    try:
        with open(caminho_saida, "r", encoding="utf-8") as f:
            html = f.read()

        # cria gradiente com varios pontos (0%,25%,50%,75%,100%) usando o colormap
        try:
            stops = [gmin, gmin + 0.25 * (gmax - gmin), gmin + 0.5 * (gmax - gmin), gmin + 0.75 * (gmax - gmin), gmax]
            colors_stops = [map_color(s) for s in stops]
            gradient_css = ", ".join([f"{c} {i*25}%" for i, c in enumerate(colors_stops)])
        except Exception:
            gradient_css = f"{map_color(gmin)} 0%, {map_color(gmax)} 100%"
        
        # Removido controles de zoom e navegação
        
        legenda_html = f"""
<style>
  .legend {{
    position: fixed;
    right: 16px;
    top: 16px;
    z-index: 9998;
    background: rgba(255,255,255,0.96);
    padding: 10px 12px;
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    font-family: Arial, Helvetica, sans-serif;
    font-size: 12px;
    color: #111;
    min-width: 160px;
  }}
  .legend .bar {{
    height: 14px;
    border-radius: 8px;
    background: linear-gradient(90deg, {gradient_css});
    margin: 8px 0 6px 0;
  }}
  .legend .ticks {{
    display:flex; justify-content:space-between; font-size:11px; color:#444; margin-top:4px;
  }}
</style>
<div class="legend">
  <div style="font-weight:600; margin-bottom:4px;">Legenda — Grau (conexões)</div>
  <div style="font-size:11px; color:#555;">Escala de calor: mais conexões = cor mais quente</div>
  <div class="bar"></div>
  <div class="ticks">
    <div>{stops[0]:.0f}</div>
    <div>{stops[1]:.0f}</div>
    <div>{stops[2]:.0f}</div>
    <div>{stops[3]:.0f}</div>
    <div>{stops[4]:.0f}</div>
  </div>
  <div style="font-size:11px; color:#666; margin-top:6px;">Min — Median — Max</div>
</div>
"""

        if "<body>" in html:
            html = html.replace("<body>", "<body>\n" + legenda_html, 1)

        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        # não interrompe caso falhe a inserção da legenda
        pass

def ranking_densidade_ego_microrregiao_png():
    """
    Lê:
      - out/parte1/ego_bairro.csv  (densidade_ego por bairro)
      - data/bairros_unique.csv (bairro -> microrregiao)

    Calcula, para cada microrregiao, a média de densidade_ego
    e gera um gráfico de barras:

        out/parte1/ranking_densidade_ego_microrregiao.png
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os
    
    # Configurações iniciais
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    
    try:
        # 1) Lê os dados
        df_ego = pd.read_csv(os.path.join(OUT_DIR, 'ego_bairro.csv'))
        df_bairros = pd.read_csv(os.path.join(DATA_DIR, 'bairros_unique.csv'))
        
        # 2) Mescla os dados
        df = pd.merge(
            df_ego[['bairro', 'densidade_ego']],
            df_bairros[['bairro', 'microrregiao']],
            on='bairro',
            how='inner'
        )
        
        # 3) Calcula a média por microrregião
        df_media = (df.groupby('microrregiao', as_index=False)['densidade_ego']
                   .mean()
                   .sort_values('densidade_ego', ascending=False))
        
        # 4) Cria a figura
        plt.figure(figsize=(10, 6))
        
        # 5) Gera o gráfico de barras
        ax = sns.barplot(
            data=df_media,
            x='microrregiao',
            y='densidade_ego',
            palette='viridis',
            edgecolor='0.3',
            linewidth=0.5
        )
        
        # 6) Adiciona os valores nas barras
        for p in ax.patches:
            ax.annotate(
                f"{p.get_height():.2f}",
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center',
                va='center',
                xytext=(0, 5),
                textcoords='offset points',
                fontweight='bold'
            )
        
        # 7) Configurações do gráfico
        plt.title('Densidade Média das Redes Ego por Microrregião', 
                 fontsize=14, 
                 pad=20,
                 fontweight='bold')
        
        plt.xlabel('Microrregião', fontsize=12)
        plt.ylabel('Densidade Média', fontsize=12)
        
        # Rotaciona os rótulos do eixo x para melhor legibilidade
        plt.xticks(rotation=45, ha='right')
        
        # 8) Ajusta o layout e salva
        plt.tight_layout()
        
        caminho_saida = os.path.join(OUT_DIR, 'ranking_densidade_ego_microrregiao.png')
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gráfico salvo em: {caminho_saida}")
        return caminho_saida
        
    except Exception as e:
        print(f"Erro ao gerar o gráfico: {str(e)}")
        return None

def arvore_bfs_boaviagem_html():
    """
    Gera uma ÁRVORE BFS a partir do bairro 'Boa Viagem' em HTML interativo (pyvis).

    Cada nível da BFS é exibido como uma camada hierárquica:

        out/parte1/arvore_bfs_boaviagem.html
    """
    if Network is None:
        print("Pyvis (Network) não está disponível. Verifique a instalação de pyvis/jinja2.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    caminho_bairros_unique = os.path.join(DATA_DIR, "bairros_unique.csv")
    caminho_adjacencias = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

    # 1) Carrega o grafo completo
    grafo, _ = carregar_grafo_recife(
        caminho_bairros_unique,
        caminho_adjacencias
    )

    origem = "Boa Viagem"
    if origem not in grafo.obter_nos():
        raise ValueError(
            f"O bairro de origem '{origem}' não existe no grafo. "
            "Verifique a grafia em bairros_unique.csv."
        )

    # 2) Executa a BFS e obtém pai e nível de cada bairro alcançado
    pai, nivel = bfs_arvore(grafo, origem)
    
    # Calcula estatísticas da árvore
    total_nos = len(nivel)
    profundidade_max = max(nivel.values()) if nivel else 0
    
    # Conta nós por nível
    nos_por_nivel = {}
    for bairro, nv in nivel.items():
        nos_por_nivel[nv] = nos_por_nivel.get(nv, 0) + 1

    # 3) Cria a rede pyvis com layout hierárquico
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000",
        directed=True  # árvore tem direção pai -> filho
    )

    # Vamos usar as microrregiões como tooltip extra (se quiser pegar depois),
    # mas o essencial aqui é nível + conexões.

    # 4) Adiciona nós com cor diferente para a origem
    for bairro, nv in nivel.items():
        if bairro == origem:
            cor = "#ffb703"  # destaque (amarelo/laranja)
        else:
            cor = "#8ecae6"  # azul clarinho

        titulo = f"{bairro}<br>Nível BFS: {nv}"
        if pai[bairro] is not None:
            titulo += f"<br>Pai: {pai[bairro]}"

        net.add_node(
            bairro,
            label=bairro,
            title=titulo,
            level=nv,   # nível da BFS para layout hierárquico
            color=cor
        )

    # 5) Adiciona arestas pai -> filho
    for bairro, p in pai.items():
        if p is None:
            continue  # origem não tem pai
        net.add_edge(p, bairro)

    # 6) Configura layout hierárquico no vis.js
    net.set_options("""
    {
    "layout": {
        "hierarchical": {
        "enabled": true,
        "sortMethod": "directed",
        "direction": "UD",
        "nodeSpacing": 150,
        "levelSeparation": 120
        }
    },
    "physics": {
        "enabled": false
    }
    }
    """)


    caminho_saida = os.path.join("out/parte1", "arvore_bfs_boaviagem.html")
    net.show(caminho_saida, notebook=False)
    print(caminho_saida)
    
    # Adiciona controles, legenda e informações
    with open(caminho_saida, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Prepara lista de nós por nível para exibição
    nos_por_nivel_html = ""
    for nv in sorted(nos_por_nivel.keys()):
        nos_por_nivel_html += f'<div>Nível {nv}: {nos_por_nivel[nv]} bairro(s)</div>'
    
    # Prepara opções de destaque de nível
    opcoes_nivel = ""
    for nv in sorted(nos_por_nivel.keys()):
        opcoes_nivel += f'<option value="{nv}">Nível {nv}</option>'
    
    info_html = f"""
<style>
  .info-panel {{
    position: fixed;
    top: 16px;
    left: 16px;
    z-index: 9998;
    background: rgba(255,255,255,0.96);
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    font-family: Arial, Helvetica, sans-serif;
    font-size: 12px;
    color: #111;
    min-width: 200px;
    max-width: 280px;
    max-height: 85vh;
    overflow-y: auto;
  }}
  .info-panel h3 {{
    margin: 0 0 10px 0;
    font-size: 14px;
    color: #333;
  }}
  .info-section {{
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
  }}
  .info-section:last-child {{
    border-bottom: none;
  }}
  .info-item {{
    margin: 6px 0;
    font-size: 11px;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    margin: 6px 0;
    font-size: 11px;
  }}
  .legend-color {{
    width: 16px;
    height: 16px;
    border-radius: 3px;
    margin-right: 8px;
    border: 1px solid rgba(0,0,0,0.2);
  }}
  .level-select {{
    width: 100%;
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 11px;
    margin-top: 6px;
  }}
  .level-select:focus {{
    outline: none;
    border-color: #4CAF50;
  }}
  .zoom-section {{
    display: flex;
    gap: 4px;
    margin-top: 8px;
  }}
  .zoom-section button {{
    flex: 1;
    padding: 6px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    font-size: 11px;
    transition: background 0.2s;
  }}
  .zoom-section button:hover {{
    background: #e0e0e0;
  }}
  .nav-section {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    margin-top: 8px;
  }}
  .nav-row {{
    display: flex;
    gap: 2px;
    justify-content: center;
  }}
  .nav-btn {{
    background: #f0f0f0;
    border: 1px solid #ccc;
    padding: 4px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
  }}
  .controls-box {{
    position: absolute;
    top: 10px;
    right: 10px;
    width: 300px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    z-index: 1000;
    font-family: Arial, sans-serif;
    max-height: 90vh;
    overflow-y: auto;
  }}
  .controls-vertical {{
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }}
  .section-title {{
    font-weight: bold;
    color: #333;
    font-size: 14px;
    margin-top: 8px;
    margin-bottom: 4px;
    padding-bottom: 4px;
    border-bottom: 1px solid #eee;
  }}
  .stats-box {{
    background: #f9f9f9;
    border-radius: 4px;
    padding: 8px;
    font-size: 13px;
    margin-bottom: 8px;
  }}
  .legend-box {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 8px;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    font-size: 12px;
  }}
  .legend-color {{
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    border: 1px solid #999;
  }}
  .zoom-controls {{
    display: flex;
    gap: 4px;
    margin-bottom: 8px;
  }}
  .zoom-controls button {{
    flex: 1;
    padding: 6px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
  }}
  .navigation-controls {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }}
  .nav-btn {{
    width: 30px;
    height: 30px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
  }}
  .nav-btn:hover {{
    background: #e0e0e0;
  }}
  .nav-btn.center {{
    font-size: 10px;
  }}
  .nav-row {{
    display: flex;
    gap: 8px;
    justify-content: center;
    width: 100%;
  }}
  select, button {{
    width: 100%;
    padding: 6px;
    margin-bottom: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 12px;
  }}
  button {{
    background: #f0f0f0;
    cursor: pointer;
  }}
  button:hover {{
    background: #e0e0e0;
  }}
</style>

<script>
var nivelData = __NIVEL_DATA__;
var originalColors = {{}};

function highlightLevel() {{
    var select = document.getElementById('level-select');
    var selectedLevel = select.value;
    
    if (!selectedLevel) return;
    
    var level = parseInt(selectedLevel);
    var allNodes = nodes.get();
    
    // Salva cores originais se ainda não salvou
    for (var i = 0; i < allNodes.length; i++) {{
        var n = allNodes[i];
        if (!originalColors[n.id]) {{
            originalColors[n.id] = n.color;
        }}
    }}
    
    // Destaca nós do nível selecionado
    for (var i = 0; i < allNodes.length; i++) {{
        var n = allNodes[i];
        var nodeLevel = nivelData[n.id];
        if (nodeLevel === level) {{
            n.color = {{ background: '#ff6b6b', border: '#c92a2a' }};
        }} else {{
            n.color = originalColors[n.id];
        }}
    }}
    nodes.update(allNodes);
}}

function resetHighlight() {{
    var allNodes = nodes.get();
    for (var i = 0; i < allNodes.length; i++) {{
        var n = allNodes[i];
        if (originalColors[n.id]) {{
            n.color = originalColors[n.id];
        }}
    }}
    nodes.update(allNodes);
    document.getElementById('level-select').value = '';
}}

function zoomIn() {{
    var scale = network.getScale();
    network.moveTo({{
        scale: Math.min(scale * 1.3, 5),
        animation: {{ duration: 300 }}
    }});
}}
function zoomOut() {{
    var scale = network.getScale();
    network.moveTo({{
        scale: Math.max(scale / 1.3, 0.1),
        animation: {{ duration: 300 }}
    }});
}}
function resetZoom() {{
    network.fit({{
        animation: {{ duration: 600, easingFunction: 'easeInOutQuad' }}
    }});
}}
function moveView(direction) {{
    var moveAmount = 100;
    var position = network.getViewPosition();
    var scale = network.getScale();
    
    if (!position) {{
        position = {{ x: 0, y: 0 }};
    }}
    
    var newPosition = {{ x: position.x, y: position.y }};
    
    switch(direction) {{
        case 'up':
            newPosition.y -= moveAmount;
            break;
        case 'down':
            newPosition.y += moveAmount;
            break;
        case 'left':
            newPosition.x -= moveAmount;
            break;
        case 'right':
            newPosition.x += moveAmount;
            break;
        case 'center':
            network.fit({{
                animation: {{ duration: 400, easingFunction: 'easeInOutQuad' }}
            }});
            return;
    }}
    
    network.moveTo({{
        position: newPosition,
        scale: scale,
        animation: {{ duration: 300, easingFunction: 'easeInOutQuad' }}
    }});
}}
</script>
"""
    
    # Prepara dados JSON para JavaScript
    nivel_data_js = json.dumps(nivel, ensure_ascii=False)
    info_html = info_html.replace("__NIVEL_DATA__", nivel_data_js)
    
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + info_html, 1)
    
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)


def grafo_interativo_html():
    """
    Gera um HTML interativo com:
        - Tooltip por bairro: grau, microrregiao, densidade_ego
        - Caixa de busca por bairro
        - Botao para destacar o caminho 'Nova Descoberta -> Boa Viagem (Setubal)'

    Saida: out/parte1/grafo_interativo.html
    """
    if Network is None:
        print("Pyvis (Network) nao esta disponivel. Verifique a instalacao de pyvis/jinja2.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    # --- 1) Carrega o grafo completo de bairros + microrregiao ---
    caminho_bairros_unique = os.path.join(DATA_DIR, "bairros_unique.csv")
    caminho_adjacencias = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

    grafo, bairro_para_micro = carregar_grafo_recife(
        caminho_bairros_unique,
        caminho_adjacencias
    )

    bairros = grafo.obter_nos()

    # --- Verificação: leia data/bairros_unique.csv e compare com o mapeamento do grafo
    issues = []
    try:
        if os.path.exists(caminho_bairros_unique):
            df_bairros_unique = pd.read_csv(caminho_bairros_unique)
            df_bairros_unique.columns = df_bairros_unique.columns.str.strip().str.lower()
            if {"bairro", "microrregiao"}.issubset(df_bairros_unique.columns):
                csv_map = {row["bairro"]: str(row["microrregiao"]) for _, row in df_bairros_unique.iterrows()}
                # bairros no grafo que nao estao no csv
                missing_in_csv = [b for b in bairros if b not in csv_map]
                if missing_in_csv:
                    issues.append(f"Bairros no grafo ausentes em bairros_unique.csv: {missing_in_csv}")
                # bairros no csv que nao estao no grafo (informativo)
                missing_in_graph = [b for b in csv_map.keys() if b not in bairros]
                if missing_in_graph:
                    issues.append(f"Bairros no CSV ausentes no grafo: {missing_in_graph[:10]}{'...' if len(missing_in_graph)>10 else ''}")
                # divergências de microrregiao
                mismatches = []
                for b in bairros:
                    if b in csv_map:
                        gmic = str(bairro_para_micro.get(b, "NA"))
                        cmic = csv_map[b]
                        if gmic != cmic:
                            mismatches.append((b, gmic, cmic))
                if mismatches:
                    issues.append(f"Divergencias microrregiao (bairro, grafo, csv): {mismatches}")
            else:
                issues.append("Arquivo bairros_unique.csv nao tem colunas 'bairro' e 'microrregiao'.")
        else:
            issues.append(f"Arquivo de referencia {caminho_bairros_unique} nao encontrado.")
    except Exception as e:
        issues.append(f"Erro ao validar bairros_unique.csv: {e}")

    # --- 2) Carrega grau por bairro (mantemos apenas para tooltip, mas nao usaremos para tamanho) ---
    caminho_graus = os.path.join(OUT_DIR, "graus.csv")
    if not os.path.exists(caminho_graus):
        raise FileNotFoundError(
            f"Arquivo de graus nao encontrado: {caminho_graus}. "
            f"Certifique-se de ter gerado graus.csv (passo 4)."
        )

    df_graus = pd.read_csv(caminho_graus)
    df_graus.columns = df_graus.columns.str.strip().str.lower()
    if not {"bairro", "grau"}.issubset(df_graus.columns):
        raise ValueError("graus.csv deve ter as colunas 'bairro' e 'grau'.")

    graus = {row["bairro"]: int(row["grau"]) for _, row in df_graus.iterrows()}

    # --- 3) Carrega densidade_ego por bairro (out/parte1/ego_bairro.csv) ---
    caminho_ego = os.path.join(OUT_DIR, "ego_bairro.csv")
    if not os.path.exists(caminho_ego):
        raise FileNotFoundError(
            f"Arquivo ego_bairro.csv nao encontrado em {caminho_ego}. "
            f"Certifique-se de ter gerado ego_bairro.csv (passo 3)."
        )

    df_ego = pd.read_csv(caminho_ego)
    df_ego.columns = df_ego.columns.str.strip().str.lower()
    if not {"bairro", "densidade_ego"}.issubset(df_ego.columns):
        raise ValueError(
            "ego_bairro.csv deve ter as colunas 'bairro' e 'densidade_ego'."
        )

    dens_ego = {row["bairro"]: float(row["densidade_ego"]) for _, row in df_ego.iterrows()}

    # --- 4) Carrega o caminho Nova Descoberta -> Boa Viagem (Setubal) (passo 6) ---
    caminho_json = os.path.join(OUT_DIR, "percurso_nova_descoberta_setubal.json")
    path_nodes = []
    path_edges = []

    if os.path.exists(caminho_json):
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)

        caminho = dados.get("caminho") or dados.get("caminho_bairros") or []
        if isinstance(caminho, list) and len(caminho) >= 2:
            path_nodes = caminho
            for i in range(len(caminho) - 1):
                u = caminho[i]
                v = caminho[i + 1]
                path_edges.append([u, v])
    else:
        print("Aviso: JSON do percurso Nova Descoberta -> Setubal nao encontrado. "
                "Botoes de destaque do caminho ainda serao gerados, mas nao terao efeito.")

    # --- 5) Paleta por microrregiao (até 6 esperadas) ---
    palette = [
        "#1f77b4",  # azul
        "#ff7f0e",  # laranja
        "#2ca02c",  # verde
        "#d62728",  # vermelho
        "#9467bd",  # roxo
        "#8c564b"   # marrom
    ]

    unique_micros = []
    for b, m in bairro_para_micro.items():
        ms = str(m)
        if ms not in unique_micros:
            unique_micros.append(ms)

    micro_to_color = {m: palette[i % len(palette)] for i, m in enumerate(unique_micros)}
    default_node_color = "#97c2fc"
    
    # --- 5.1) Calcula estatísticas do grafo ---
    total_bairros = grafo.ordem()
    total_conexoes = grafo.tamanho()
    densidade_media = grafo.densidade()
    
    # Ordena microrregiões para legenda
    unique_micros_sorted = sorted(unique_micros, key=lambda x: int(x) if x.isdigit() else 999)

    # --- 6) Cria a rede pyvis com opções para rótulos maiores ---
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000"
    )
    net.barnes_hut()

    # força fonte e tamanho de nó padrão via opções do vis.js para legibilidade
    net.set_options('''{
        "nodes": { "font": { "size": 14, "face": "Arial" } },
        "edges": { "smooth": false },
        "physics": { "stabilization": { "enabled": true, "iterations": 1000 } },
        "interaction": {
            "dragNodes": true,
            "dragView": true,
            "zoomView": true,
            "navigationButtons": false,
            "keyboard": true
        }
    }''')

    # --- 7) Adiciona nos com tooltip (GRAU apenas no tooltip; tamanho UNIFORME) ---
    NODE_SIZE = 14
    for bairro in bairros:
        grau = graus.get(bairro, grafo.grau(bairro))
        microrregiao = bairro_para_micro.get(bairro, "NA")
        microrregiao_key = str(microrregiao)
        dens = dens_ego.get(bairro, None)
        if dens is None or pd.isna(dens):
            dens_str = "-"
        else:
            dens_str = f"{dens:.4f}"

        title = (
            f"Bairro: {bairro}<br>"
            f"Grau: {grau}<br>"
            f"Microrregiao: {microrregiao_key}<br>"
            f"Densidade ego: {dens_str}"
        )

        cor = micro_to_color.get(microrregiao_key, default_node_color)

        font = {"size": 14, "face": "Arial", "strokeWidth": 0}

        net.add_node(
            bairro,
            label=bairro,
            title=title,
            color={"background": cor, "border": "#222222"},
            size=NODE_SIZE,
            font=font
        )

    # --- 8) Adiciona arestas do grafo (sem duplicar), coloridas por microrregiao quando possível ---
    arestas_adicionadas = set()
    for b in bairros:
        for vizinho, peso in grafo.vizinhos(b):
            aresta = tuple(sorted((b, vizinho)))
            if aresta in arestas_adicionadas:
                continue

            m1 = str(bairro_para_micro.get(b, "NA"))
            m2 = str(bairro_para_micro.get(vizinho, "NA"))
            if m1 == m2 and m1 in micro_to_color:
                edge_color = micro_to_color[m1]
            else:
                edge_color = "#cfcfcf"

            # largura uniforme para todas as arestas
            # removemos 'value' para evitar que o vis.js escale larguras
            net.add_edge(b, vizinho, color=edge_color, width=2)
            arestas_adicionadas.add(aresta)

    # --- 9) Gera o HTML base com pyvis ---
    caminho_saida = os.path.join("out/parte1", "grafo_interativo.html")
    net.show(caminho_saida, notebook=False)
    print(caminho_saida)

    # --- 10) Pos-processa o HTML para adicionar busca + botoes + JS de destaque ---
    with open(caminho_saida, "r", encoding="utf-8") as f:
        html = f.read()

    # Prepara controles do grafo
    issues_html = ""
    if issues:
        items = "<br>".join([f"- {i}" for i in issues])
        issues_html = f"<div style='padding:8px;border:1px solid #faa; background:#fff0f0;margin-bottom:8px;'><strong>Atenção:</strong><br>{items}</div>"

    # Lista de bairros para os selects
    bairros_sorted = sorted(bairros)
    bairros_options = "\n".join([f"                <option value='{b}'>{b}</option>" for b in bairros_sorted])
    
    # Legenda de cores por microrregião
    legend_items = "\n".join([
        f'            <div class="legend-item"><span class="legend-color" style="background-color: {micro_to_color.get(m, default_node_color)}"></span> Microrregião {m}</div>'
        for m in unique_micros_sorted
    ])
    
    # Checkboxes para filtrar microrregiões
    filter_checkboxes = "\n".join([
        f'            <label class="filter-item"><input type="checkbox" class="micro-filter" value="{m}" checked onchange="toggleMicrorregiao(\'{m}\')"><span class="filter-color" style="background-color: {micro_to_color.get(m, default_node_color)}"></span> Microrregião {m}</label>'
        for m in unique_micros_sorted
    ])
    
    controls_html = f"""
<style>
    .controls-box {{
        position: fixed;
        top: 16px;
        left: 16px;
        z-index: 9999;
        background: linear-gradient(180deg, #0b0b0b 0%, #1a1a1a 100%);
        color: #ffffff;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        min-width: 240px;
        max-width: 340px;
        max-height: 90vh;
        overflow-y: auto;
        font-family: Arial, Helvetica, sans-serif;
    }}
    .controls-box::-webkit-scrollbar {{
        width: 6px;
    }}
    .controls-box::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.1);
        border-radius: 3px;
    }}
    .controls-box::-webkit-scrollbar-thumb {{
        background: rgba(255,255,255,0.3);
        border-radius: 3px;
    }}
    .controls-box .issue {{
        background: rgba(255,80,80,0.08);
        border: 1px solid rgba(255,80,80,0.18);
        color: #ffdede;
        padding: 6px 8px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-size: 12px;
    }}
    .controls-vertical {{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .section-title {{
        font-size: 13px;
        font-weight: 600;
        color: #aaa;
        margin-top: 8px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .controls-vertical input[type="text"] {{
        width: 100%;
        padding: 10px 12px;
        border-radius: 8px;
        border: 2px solid rgba(255,255,255,0.2);
        background: rgba(30, 30, 30, 0.95);
        color: #ffffff;
        outline: none;
        font-size: 14px;
        box-sizing: border-box;
        margin-bottom: 4px;
    }}
    .controls-vertical input[type="text"]:focus {{
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }}
    .controls-vertical select {{
        width: 100%;
        padding: 10px 12px;
        border-radius: 8px;
        border: 2px solid rgba(255,255,255,0.2);
        background: rgba(30, 30, 30, 0.95);
        color: #ffffff;
        outline: none;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-sizing: border-box;
    }}
    .controls-vertical select:hover {{
        border-color: rgba(255,255,255,0.4);
        background: rgba(40, 40, 40, 0.95);
    }}
    .controls-vertical select:focus {{
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }}
    .controls-vertical select option {{
        background: #2a2a2a;
        color: #ffffff;
        padding: 8px;
    }}
    .controls-vertical button {{
        background: linear-gradient(180deg, #222 0%, #111 100%);
        color: #fff;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 8px 10px;
        border-radius: 8px;
        cursor: pointer;
        text-align: left;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        transition: transform 0.08s ease, box-shadow 0.08s ease;
        font-size: 14px;
        margin-bottom: 4px;
    }}
    .controls-vertical button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.6);
    }}
    .controls-vertical button:active {{
        transform: translateY(0);
    }}
    .stats-box {{
        background: rgba(40, 40, 40, 0.6);
        padding: 10px;
        border-radius: 8px;
        margin-top: 4px;
        font-size: 12px;
        line-height: 1.6;
    }}
    .stats-box div {{
        margin: 4px 0;
    }}
    .legend-box {{
        background: rgba(40, 40, 40, 0.6);
        padding: 10px;
        border-radius: 8px;
        margin-top: 4px;
        font-size: 12px;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        margin: 6px 0;
    }}
    .legend-color {{
        width: 16px;
        height: 16px;
        border-radius: 3px;
        margin-right: 8px;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .filter-item {{
        display: flex;
        align-items: center;
        margin: 6px 0;
        cursor: pointer;
        font-size: 12px;
        user-select: none;
    }}
    .filter-item input[type="checkbox"] {{
        margin-right: 8px;
        cursor: pointer;
    }}
    .filter-color {{
        width: 14px;
        height: 14px;
        border-radius: 3px;
        margin-right: 6px;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .path-info {{
        background: rgba(76, 175, 80, 0.15);
        border: 1px solid rgba(76, 175, 80, 0.3);
        padding: 10px;
        border-radius: 8px;
        margin-top: 8px;
        font-size: 12px;
        display: none;
    }}
    .path-info.show {{
        display: block;
    }}
    .path-info-title {{
        font-weight: 600;
        margin-bottom: 6px;
        color: #4CAF50;
    }}
    .path-info-content {{
        line-height: 1.6;
    }}
    .loading {{
        display: none;
        text-align: center;
        padding: 8px;
        font-size: 12px;
        color: #4CAF50;
    }}
    .loading.show {{
        display: block;
    }}
    .zoom-controls {{
        display: flex;
        gap: 4px;
        margin-top: 4px;
    }}
    .zoom-controls button {{
        flex: 1;
        padding: 6px;
        font-size: 12px;
        text-align: center;
    }}
    .navigation-controls {{
        margin-top: 4px;
    }}
    .nav-btn {{
        background: linear-gradient(180deg, #222 0%, #111 100%);
        color: #fff;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 8px;
        border-radius: 8px;
        cursor: pointer;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        transition: transform 0.08s ease, box-shadow 0.08s ease;
        font-size: 16px;
        min-width: 40px;
        min-height: 40px;
    }}
    .nav-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.6);
    }}
    .nav-btn:active {{
        transform: translateY(0);
    }}
    @media (max-width: 480px) {{
        .controls-box {{ left: 8px; top: 8px; padding: 10px; min-width: 200px; max-width: 280px; }}
    }}
</style>

<div class="controls-box">
    {f"<div class='issue'>{issues_html}</div>" if issues_html else ""}
    <div class="controls-vertical">
        <div class="section-title">Estatísticas</div>
        <div class="stats-box">
            <div><strong>Bairros:</strong> {total_bairros}</div>
            <div><strong>Conexões:</strong> {total_conexoes}</div>
            <div><strong>Densidade:</strong> {densidade_media:.4f}</div>
        </div>
        
        <div class="section-title">Busca</div>
        <input type="text" id="busca-bairro" placeholder="Digite o nome do bairro..." onkeypress="if(event.key==='Enter') buscarBairro()">
        <div style="display: flex; gap: 4px;">
            <button onclick="buscarBairro()" style="flex: 1;">Buscar Bairro</button>
            <button onclick="limparBusca()" style="flex: 1;">Limpar Busca</button>
        </div>
        
        <div class="section-title">Caminhos</div>
        <select id="origem-select">
            <option value="">Selecione a origem...</option>
{bairros_options}
        </select>
        <select id="destino-select">
            <option value="">Selecione o destino...</option>
{bairros_options}
        </select>
        <div class="loading" id="loading-indicator">Calculando caminho...</div>
        <button onclick="calcularCaminho()">Calcular Caminho</button>
        <button onclick="highlightPath()">Destacar Nova Descoberta → Boa Viagem</button>
        <button onclick="resetHighlight()">Limpar Destaques</button>
        <div class="path-info" id="path-info">
            <div class="path-info-title">Informações do Caminho</div>
            <div class="path-info-content" id="path-info-content"></div>
        </div>
        
        <div class="section-title">Legenda</div>
        
        <div class="gp-section-title">Filtros</div>
        <div class="gp-legend-box">
{filter_checkboxes}
            <div style="margin-top: 8px;">
                <button onclick="showAllMicrorregioes()" style="font-size: 11px; padding: 6px;">Mostrar Todas</button>
                <button onclick="hideAllMicrorregioes()" style="font-size: 11px; padding: 6px;">Ocultar Todas</button>
            </div>
        </div>
        
        <div class="section-title">Zoom</div>
        <div class="zoom-controls">
            <button onclick="zoomIn()">➕</button>
            <button onclick="zoomOut()">➖</button>
            <button onclick="resetView()">Reverter</button>
        </div>
        
        <div class="section-title">Navegação</div>
        <div class="navigation-controls">
            <div style="display: flex; justify-content: center; margin-bottom: 4px;">
                <button onclick="moveView('up')" class="nav-btn">⬆️</button>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 4px;">
                <button onclick="moveView('left')" class="nav-btn">⬅️</button>
                <button onclick="moveView('center')" class="nav-btn" style="font-size: 10px;"></button>
                <button onclick="moveView('right')" class="nav-btn">➡️</button>
            </div>
            <div style="display: flex; justify-content: center; margin-top: 4px;">
                <button onclick="moveView('down')" class="nav-btn">⬇️</button>
            </div>
        </div>
    </div>
</div>
"""
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + controls_html, 1)

    # --- 10.3) Prepara dados para cálculo de menor caminho ---
    # Cria um dicionário com os dados do grafo para uso no JavaScript
    graph_data = {
        'nodes': list(bairros),
        'edges': []
    }
    
    for b in bairros:
        for vizinho, peso in grafo.vizinhos(b):
            edge = tuple(sorted((b, vizinho)))
            if edge not in graph_data['edges']:
                graph_data['edges'].append(edge)
    
    graph_data_js = json.dumps(graph_data, ensure_ascii=False)
    path_nodes_js = json.dumps(path_nodes, ensure_ascii=False)
    path_edges_js = json.dumps(path_edges, ensure_ascii=False)

    # Prepara dados de microrregiões para JavaScript
    micro_to_color_js = json.dumps(micro_to_color, ensure_ascii=False)
    bairro_to_micro_js = json.dumps({b: str(m) for b, m in bairro_para_micro.items()}, ensure_ascii=False)
    
    extra_js = """
<script type="text/javascript">
    // Nos e arestas do caminho minimo Nova Descoberta -> Boa Viagem (Setubal)
    var pathNodes = __PATH_NODES__;
    var pathEdges = __PATH_EDGES__;
    var microToColor = __MICRO_TO_COLOR__;
    var bairroToMicro = __BAIRRO_TO_MICRO__;

    // Conjunto com as arestas do caminho (chave canonica "u||v")
    var pathEdgeSet = {};
    for (var i = 0; i < pathEdges.length; i++) {
    var pe = pathEdges[i]; // pe = [u, v]
    var key = [pe[0], pe[1]].sort().join("||");
    pathEdgeSet[key] = true;
    }

    function buscarBairro() {
    var input = document.getElementById('busca-bairro');
    if (!input) return;
    var nome = input.value.trim();
    if (!nome) return;

    var allNodes = nodes.get();
    var nomeLower = nome.toLowerCase();
    var found = null;
    var matches = [];

    // Busca exata primeiro
    for (var i = 0; i < allNodes.length; i++) {
        var n = allNodes[i];
        if (n.id === nome || (n.label && n.label.toLowerCase() === nomeLower)) {
        found = n;
        break;
        }
        // Também coleta correspondências parciais
        if (n.label && n.label.toLowerCase().includes(nomeLower)) {
            matches.push(n);
        }
    }

    if (!found) {
        if (matches.length === 0) {
            alert("Bairro não encontrado: " + nome);
            return;
        } else if (matches.length === 1) {
            found = matches[0];
        } else {
            // Múltiplas correspondências - destaca todas
            var matchIds = matches.map(function(n) { return n.id; });
            network.selectNodes(matchIds);
            network.fit({
                nodes: matchIds,
                animation: { duration: 800, easingFunction: 'easeInOutQuad' }
            });
            return;
        }
    }

    network.selectNodes([found.id]);
    network.focus(found.id, {
        scale: 1.6,
        animation: { duration: 800, easingFunction: 'easeInOutQuad' }
    });
    }
    
    function limparBusca() {
        // Limpa o campo de input
        var input = document.getElementById('busca-bairro');
        if (input) {
            input.value = '';
        }
        
        // Desseleciona todos os nós
        network.unselectAll();
        
        // Reseta a visualização para o estado padrão
        network.fit({
            animation: { duration: 600, easingFunction: 'easeInOutQuad' }
        });
    }
    
    function showPathInfo(path, distance, algoritmo) {
        var pathInfo = document.getElementById('path-info');
        var pathInfoContent = document.getElementById('path-info-content');
        if (!pathInfo || !pathInfoContent) return;
        
        var steps = path.length - 1;
        var pathList = path.join(' → ');
        var algoritmoNome = algoritmo || 'Algoritmo';
        
        pathInfoContent.innerHTML = 
            '<div><strong>Algoritmo:</strong> ' + algoritmoNome + '</div>' +
            '<div><strong>Distância:</strong> ' + distance + ' conexões</div>' +
            '<div><strong>Passos:</strong> ' + steps + '</div>' +
            '<div style="margin-top: 6px; font-size: 11px; color: #aaa; max-height: 100px; overflow-y: auto;">' +
            '<strong>Rota:</strong><br>' + pathList +
            '</div>';
        
        pathInfo.classList.add('show');
    }
    
    function hidePathInfo() {
        var pathInfo = document.getElementById('path-info');
        if (pathInfo) {
            pathInfo.classList.remove('show');
        }
    }
    
    function showLoading() {
        var loading = document.getElementById('loading-indicator');
        if (loading) loading.classList.add('show');
    }
    
    function hideLoading() {
        var loading = document.getElementById('loading-indicator');
        if (loading) loading.classList.remove('show');
    }
    
    function toggleMicrorregiao(micro) {
        var checkbox = document.querySelector('.micro-filter[value="' + micro + '"]');
        if (!checkbox) return;
        
        var allNodes = nodes.get();
        var color = microToColor[micro] || '#97c2fc';
        var show = checkbox.checked;
        
        for (var i = 0; i < allNodes.length; i++) {
            var n = allNodes[i];
            var nodeMicro = bairroToMicro[n.id];
            if (nodeMicro === micro) {
                if (show) {
                    // Restaurar cor original
                    if (n._originalColor) {
                        n.color = n._originalColor;
                    } else {
                        n.color = { background: color, border: '#222222' };
                    }
                } else {
                    // Define a cor como cinza-claro
                    if (!n._originalColor) {
                        n._originalColor = n.color;
                    }
                    n.color = { 
                        background: '#D3D3D3',  // Cinza claro
                        border: '#A9A9A9',      // Cinza mais escuro para a borda
                        highlight: { background: '#C0C0C0', border: '#808080' }
                    };
                }
            }
        }
        nodes.update(allNodes);
        
        // Atualiza as arestas para ficarem mais claras quando a região estiver desmarcada
        var allEdges = edges.get();
        for (var i = 0; i < allEdges.length; i++) {
            var e = allEdges[i];
            var fromMicro = bairroToMicro[e.from];
            var toMicro = bairroToMicro[e.to];
            if (fromMicro === micro || toMicro === micro) {
                if (show) {
                    if (e._originalColor) {
                        e.color = e._originalColor;
                    }
                } else {
                    if (!e._originalColor) {
                        e._originalColor = e.color;
                    }
                    e.color = { 
                        color: '#D3D3D3',  // Cinza claro
                        highlight: '#A9A9A9',
                        hover: '#C0C0C0',
                        opacity: 0.5
                    };
                }
            }
        }
        edges.update(allEdges);
    }
    
    function showAllMicrorregioes() {
        var checkboxes = document.querySelectorAll('.micro-filter');
        checkboxes.forEach(function(cb) {
            if (!cb.checked) {
                cb.checked = true;
                toggleMicrorregiao(cb.value);
            }
        });
    }
    
    function hideAllMicrorregioes() {
        var checkboxes = document.querySelectorAll('.micro-filter');
        checkboxes.forEach(function(cb) {
            if (cb.checked) {
                cb.checked = false;
                toggleMicrorregiao(cb.value);
            }
        });
    }
    
    function zoomIn() {
        var scale = network.getScale();
        network.moveTo({
            scale: Math.min(scale * 1.3, 5),
            animation: { duration: 300 }
        });
    }
    
    function zoomOut() {
        var scale = network.getScale();
        network.moveTo({
            scale: Math.max(scale / 1.3, 0.1),
            animation: { duration: 300 }
        });
    }
    
    function resetView() {
        network.fit({
            animation: { duration: 800, easingFunction: 'easeInOutQuad' }
        });
    }
    
    function moveView(direction) {
        var moveAmount = 100; // pixels a mover
        var position = network.getViewPosition();
        var scale = network.getScale();
        
        if (!position) {
            position = { x: 0, y: 0 };
        }
        
        var newPosition = { x: position.x, y: position.y };
        
        switch(direction) {
            case 'up':
                newPosition.y -= moveAmount;
                break;
            case 'down':
                newPosition.y += moveAmount;
                break;
            case 'left':
                newPosition.x -= moveAmount;
                break;
            case 'right':
                newPosition.x += moveAmount;
                break;
            case 'center':
                // Centraliza a visualização
                network.fit({
                    animation: { duration: 400, easingFunction: 'easeInOutQuad' }
                });
                return;
        }
        
        network.moveTo({
            position: newPosition,
            scale: scale,
            animation: { duration: 300, easingFunction: 'easeInOutQuad' }
        });
    }
    
    function calcularCaminho() {
        var origemSelect = document.getElementById('origem-select');
        var destinoSelect = document.getElementById('destino-select');
        
        if (!origemSelect || !destinoSelect) {
            alert('Elementos não encontrados');
            return;
        }
        
        var origem = origemSelect.value;
        var destino = destinoSelect.value;
        
        if (!origem || !destino) {
            alert('Selecione origem e destino');
            return;
        }
        
        // Mostra o indicador de carregamento
        showLoading();
        
        // Reseta o destaque atual
        resetHighlight();
        
        // Usa setTimeout para permitir que o loading apareça antes do cálculo pesado
        setTimeout(function() {
            calcularCaminhoDijkstra(origem, destino);
            hideLoading();
        }, 50);
    }
    
    function calcularCaminhoDijkstra(origem, destino) {
        // Implementação de Dijkstra para encontrar o menor caminho
        var graphData = __GRAPH_DATA__;
        
        // Construir mapa de adjacência com pesos
        var adjMap = {};
        for (var i = 0; i < graphData.edges.length; i++) {
            var edge = graphData.edges[i];
            var u = edge[0];
            var v = edge[1];
            if (!adjMap[u]) adjMap[u] = [];
            if (!adjMap[v]) adjMap[v] = [];
            // Assumindo peso 1 para todas as arestas
            adjMap[u].push({node: v, weight: 1});
            adjMap[v].push({node: u, weight: 1});
        }
        
        // Algoritmo de Dijkstra
        var dist = {};
        var parent = {};
        var visited = {};
        var queue = [];
        
        // Inicialização
        for (var j = 0; j < graphData.nodes.length; j++) {
            var node = graphData.nodes[j];
            dist[node] = Infinity;
            parent[node] = null;
            visited[node] = false;
        }
        
        dist[origem] = 0;
        queue.push({node: origem, dist: 0});
        
        while (queue.length > 0) {
            // Encontrar o nó com menor distância
            queue.sort(function(a, b) { return a.dist - b.dist; });
            var current = queue.shift();
            
            if (visited[current.node]) continue;
            visited[current.node] = true;
            
            if (current.node === destino) break;
            
            var neighbors = adjMap[current.node] || [];
            for (var k = 0; k < neighbors.length; k++) {
                var neighbor = neighbors[k];
                var alt = dist[current.node] + neighbor.weight;
                
                if (alt < dist[neighbor.node]) {
                    dist[neighbor.node] = alt;
                    parent[neighbor.node] = current.node;
                    queue.push({node: neighbor.node, dist: alt});
                }
            }
        }
        
        if (dist[destino] === Infinity) {
            alert('Não foi encontrado um caminho entre ' + origem + ' e ' + destino);
            return;
        }
        
        // Reconstruir o caminho
        var path = [];
        var current = destino;
        while (current !== null) {
            path.unshift(current);
            current = parent[current];
        }
        
        // Destacar caminho
        destacarCaminho(path, dist[destino]);
        
        // Mostrar informações do caminho
        showPathInfo(path, dist[destino], 'Dijkstra');
    }
    
    function destacarCaminho(path, distancia) {
        // Limpa destaques anteriores (apenas cores, sem resetar visualização)
        resetHighlightColors();
        
        // Criar conjunto de arestas do caminho
        var pathEdgeSet = {};
        for (var k = 0; k < path.length - 1; k++) {
            var key = [path[k], path[k+1]].sort().join("||");
            pathEdgeSet[key] = true;
        }
        
        var allEdges = edges.get();
        var allNodes = nodes.get();
        
        // Destacar arestas do caminho
        for (var i = 0; i < allEdges.length; i++) {
            var e = allEdges[i];
            var key = [e.from, e.to].sort().join("||");
            if (pathEdgeSet[key]) {
                if (e._originalColor === undefined) e._originalColor = e.color;
                e.color = { color: '#FF69B4' };  // rosa para o caminho
            } else {
                if (e._originalColor === undefined) e._originalColor = e.color;
                e.color = { color: '#e6e6e6' };
            }
        }
        edges.update(allEdges);
        
        // Destacar nós do caminho
        for (var i = 0; i < allNodes.length; i++) {
            var n = allNodes[i];
            if (path.indexOf(n.id) !== -1) {
                if (n._originalColor === undefined) n._originalColor = n.color;
                n.color = { background: '#FFB6C1', border: '#FF1493' }; // rosa claro para os nós
            } else {
                if (n._originalColor === undefined) n._originalColor = n.color;
            }
        }
        nodes.update(allNodes);
        
        // Centralizar no caminho (com pequeno delay para garantir que as atualizações sejam processadas)
        setTimeout(function() {
            network.fit({
                nodes: path,
                animation: { duration: 800, easingFunction: 'easeInOutQuad' }
            });
        }, 100);
    }

    function resetHighlightColors() {
        // Reset apenas das cores (sem resetar visualização)
        var allEdges = edges.get();
        for (var i = 0; i < allEdges.length; i++) {
            var e = allEdges[i];
            if (e._originalColor !== undefined) {
                e.color = e._originalColor;
            }
        }
        edges.update(allEdges);

        var allNodes = nodes.get();
        for (var i = 0; i < allNodes.length; i++) {
            var n = allNodes[i];
            if (n._originalColor !== undefined) {
                n.color = n._originalColor;
            }
        }
        nodes.update(allNodes);
    }
    
    function resetHighlight() {
        // Reset completo: cores + visualização + informações
        resetHighlightColors();
        
        // Ocultar informações do caminho
        hidePathInfo();
        
        // Resetar visualização para o padrão (igual ao botão de reset)
        network.fit({
            animation: { duration: 800, easingFunction: 'easeInOutQuad' }
        });
    }

    function highlightPath() {
    if (!pathNodes || pathNodes.length === 0) {
        alert("Caminho Nova Descoberta → Boa Viagem (Setúbal) não encontrado nos dados.");
        return;
    }

    // Limpa quaisquer destaques anteriores (apenas cores, sem resetar visualização)
    resetHighlightColors();

    // 1) DESTACAR APENAS AS ARESTAS QUE ESTAO EM pathEdgeSet (Muda apenas a cor)
    var allEdges = edges.get();
    for (var i = 0; i < allEdges.length; i++) {
        var e = allEdges[i];
        var key = [e.from, e.to].sort().join("||");
        if (pathEdgeSet[key]) {
        if (e._originalColor === undefined) e._originalColor = e.color;
        e.color = { color: '#FF69B4' };  // rosa
        } else {
        if (e._originalColor === undefined) e._originalColor = e.color;
        e.color = { color: '#e6e6e6' };
        }
    }
    edges.update(allEdges);

    // 2) DESTACAR OS NOS QUE ESTAO EM pathNodes (Muda apenas a cor, NAO o tamanho)
    var allNodes = nodes.get();
    for (var i = 0; i < allNodes.length; i++) {
        var n = allNodes[i];
        if (pathNodes.indexOf(n.id) !== -1) {
        if (n._originalColor === undefined) n._originalColor = n.color;
        n.color = { background: '#FFB6C1', border: '#FF1493' }; // rosa
        } else {
        if (n._originalColor === undefined) n._originalColor = n.color;
        // podemos deixar o restante igual (sem alterar tamanho)
        }
    }
    nodes.update(allNodes);

    // 3) Centraliza o grafo em torno dos nos do caminho (com pequeno delay)
    setTimeout(function() {
        network.fit({
            nodes: pathNodes,
            animation: { duration: 800, easingFunction: 'easeInOutQuad' }
        });
    }, 100);
    }
</script>
"""

    extra_js = extra_js.replace("__PATH_NODES__", path_nodes_js)
    extra_js = extra_js.replace("__PATH_EDGES__", path_edges_js)
    extra_js = extra_js.replace("__GRAPH_DATA__", graph_data_js)
    extra_js = extra_js.replace("__MICRO_TO_COLOR__", micro_to_color_js)
    extra_js = extra_js.replace("__BAIRRO_TO_MICRO__", bairro_to_micro_js)

    if "</body>" in html:
        html = html.replace("</body>", extra_js + "\n</body>", 1)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)

    print("Grafo interativo salvo em:", caminho_saida)


def gerar_histograma_graus():
    """
    Gera um histograma da distribuição dos graus dos bairros.
    
    Usa o arquivo out/parte1/graus.csv já gerado no passo 4.
    
    Saída: out/parte1/distribuicao_graus.png
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    import os
    
    # Garante que o diretório de saída existe
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # Lê os dados de grau
    df_graus = pd.read_csv(os.path.join(OUT_DIR, 'graus.csv'))
    
    # Configura o estilo do gráfico
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    # Cria o histograma com KDE
    ax = sns.histplot(data=df_graus, x='grau', bins=15, kde=True, color='#1f77b4')
    
    # Configurações do gráfico
    plt.title('Distribuição dos Graus dos Bairros', fontsize=16, pad=20)
    plt.xlabel('Grau do Vértice (Número de Coneexões)', fontsize=12)
    plt.ylabel('Frequência', fontsize=12)
    
    # Adiciona linhas de grade para melhor leitura
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Ajusta o layout
    plt.tight_layout()
    
    # Salva a figura
    caminho_saida = os.path.join(OUT_DIR, 'distribuicao_graus.png')
    plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Gera um arquivo de notas explicativas
    notas = """
    NOTAS EXPLICATIVAS DAS VISUALIZAÇÕES
    
    1. MAPA DE GRAUS (mapa_graus.html)
       - Visualização interativa onde cada nó representa um bairro
       - A intensidade da cor azul indica o grau do vértice (número de conexões)
       - Bairros mais conectados aparecem em azul mais escuro
       
    2. RANKING DE DENSIDADE POR MICRORREGIÃO (ranking_densidade_ego_microrregiao.png)
       - Gráfico de barras mostrando a densidade média das redes ego por microrregião
       - Ajuda a identificar quais regiões têm bairros com redes mais coesas
       
    3. SUBGRAFO DOS BAIRROS MAIS CONECTADOS (grafo_interativo.html)
       - Visualização interativa dos 10 bairros com maior grau
       - Permite explorar as conexões entre os bairros mais centrais da rede
       
    4. DISTRIBUIÇÃO DOS GRAUS (distribuicao_graus.png)
       - Histograma mostrando a frequência de cada grau na rede
       - A linha azul suave (KDE) ajuda a visualizar a distribuição
       - Revela se a rede segue uma distribuição livre de escala ou se há uma concentração em determinados graus
       
    5. ÁRVORE BFS A PARTIR DE BOA VIAGEM (arvore_bfs_boaviagem.html)
       - Mostra os níveis de distância (em saltos) a partir de Boa Viagem
       - Cada camada representa um nível de distância
       - Útil para entender a conectividade e acessibilidade dos bairros
       
    6. PERCURSO NOVA DESCOBERTA -> SETÚBAL (arvore_percurso.html)
       - Visualização do caminho mínimo entre Nova Descoberta e Setúbal
       - Destaque para o percurso encontrado pelo algoritmo
    """
    
    with open(os.path.join(OUT_DIR, 'notas_visuais.txt'), 'w', encoding='utf-8') as f:
        f.write(notas)
    
    print("Notas explicativas salvas em:", os.path.join(OUT_DIR, 'notas_visuais.txt'))
    return caminho_saida

if __name__ == "__main__":
    arvore_percurso_html()
    mapa_graus_html()
    ranking_densidade_ego_microrregiao_png()
    arvore_bfs_boaviagem_html()
    grafo_interativo_html()
    gerar_histograma_graus()
