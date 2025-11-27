import os
import json
import pandas as pd
from pyvis.network import Network
from graphs.io import carregar_grafo_ufc
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out", "parte2")

def grafo_interativo_ufc_html():
    """Gera grafo interativo dos lutadores do UFC com busca, filtros e estatísticas."""
    if Network is None:
        print("Pyvis (Network) não está disponível. Verifique a instalação de pyvis/jinja2.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    caminho_ufc = os.path.join(DATA_DIR, "total_fight_data_processado.csv")
    grafo = carregar_grafo_ufc(caminho_ufc)
    lutadores = grafo.obter_nos()
    todas_vitorias = grafo.obter_todas_vitorias()
    total_lutadores = grafo.ordem()
    total_lutas = grafo.tamanho()
    densidade_media = grafo.densidade()

    NODE_SIZE = 14
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000"
    )
    net.barnes_hut()
    net.set_options('''{
        "nodes": { 
            "font": { "size": 12, "face": "Arial" },
            "scaling": {
                "min": 10,
                "max": 30
            }
        },
        "edges": { 
            "smooth": {
                "enabled": false
            },
            "width": 1
        },
        "physics": { 
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 95,
                "springConstant": 0.04,
                "damping": 0.09,
                "avoidOverlap": 0.1
            },
            "maxVelocity": 50,
            "minVelocity": 0.75,
            "solver": "barnesHut",
            "stabilization": { 
                "enabled": true, 
                "iterations": 200,
                "updateInterval": 25,
                "onlyDynamicEdges": false,
                "fit": true
            },
            "timestep": 0.5,
            "adaptiveTimestep": true
        },
        "interaction": {
            "dragNodes": true,
            "dragView": true,
            "zoomView": true,
            "navigationButtons": false,
            "keyboard": true,
            "hover": true,
            "tooltipDelay": 200,
            "hideEdgesOnDrag": true,
            "hideEdgesOnZoom": true
        },
        "layout": {
            "improvedLayout": true,
            "clusterThreshold": 150
        }
    }''')

    for lutador in lutadores:
        grau = grafo.grau(lutador)
        vitorias = todas_vitorias.get(lutador, 0)

        title = (
            f"Lutador: {lutador}<br>"
            f"Lutas: {grau}<br>"
            f"Vitórias: {vitorias}"
        )

        if vitorias == 0:
            cor = "#e0e0e0"
        elif vitorias <= 2:
            cor = "#90caf9"
        elif vitorias <= 5:
            cor = "#42a5f5"
        elif vitorias <= 10:
            cor = "#1976d2"
        else:
            cor = "#0d47a1"

        node_size = min(10 + (grau * 0.5), 25)

        if grau >= 5:
            label = lutador
            font = {"size": 10, "face": "Arial", "strokeWidth": 0}
        else:
            label = ""
            font = {"size": 8, "face": "Arial", "strokeWidth": 0}

        net.add_node(
            lutador,
            label=label,
            title=title,
            color={"background": cor, "border": "#222222"},
            size=node_size,
            font=font,
            mass=1 + (grau * 0.1)
        )

    arestas_adicionadas = set()
    for lutador in lutadores:
        for oponente, peso in grafo.vizinhos(lutador):
            aresta = tuple(sorted((lutador, oponente)))
            if aresta in arestas_adicionadas:
                continue
            net.add_edge(
                lutador, 
                oponente, 
                color={"color": "#cfcfcf", "opacity": 0.3},
                width=0.5,
                smooth={"enabled": False}
            )
            arestas_adicionadas.add(aresta)

    caminho_saida = os.path.join(OUT_DIR, "grafo_interativo.html")
    net.show(caminho_saida, notebook=False)
    print(f"Grafo interativo salvo em: {caminho_saida}")

    with open(caminho_saida, "r", encoding="utf-8") as f:
        html = f.read()

    lutadores_sorted = sorted(lutadores)
    lutadores_options = "\n".join([f"                <option value='{l}'>{l}</option>" for l in lutadores_sorted])

    graph_data = {}
    for lutador in lutadores:
        graph_data[lutador] = {}
        for oponente, peso in grafo.vizinhos(lutador):
            graph_data[lutador][oponente] = float(peso)

    graph_data_js = json.dumps(graph_data, ensure_ascii=False)
    vitorias_map = {lutador: todas_vitorias.get(lutador, 0) for lutador in lutadores}
    vitorias_map_js = json.dumps(vitorias_map, ensure_ascii=False)

    controls_html = f"""
<style>
    .controls-box {{
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05);
        min-width: 320px;
        max-width: 380px;
        max-height: 92vh;
        overflow-y: auto;
        font-family: 'Segoe UI', Arial, sans-serif;
        backdrop-filter: blur(10px);
    }}
    
    .controls-box::-webkit-scrollbar {{
        width: 8px;
    }}
    .controls-box::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }}
    .controls-box::-webkit-scrollbar-thumb {{
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
    }}
    
    .controls-vertical {{
        display: flex;
        flex-direction: column;
        gap: 20px;
    }}
    
    .section-title {{
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #4fc3f7;
        margin: 16px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(79, 195, 247, 0.3);
    }}
    .section-title:first-child {{
        margin-top: 0;
    }}
    
    .controls-vertical input[type="text"],
    .controls-vertical select {{
        width: 100%;
        padding: 12px 14px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 10px;
        color: #ffffff;
        font-size: 14px;
        font-family: inherit;
        transition: all 0.3s ease;
        box-sizing: border-box;
        margin-bottom: 10px;
    }}
    .controls-vertical input[type="text"]:focus,
    .controls-vertical select:focus {{
        outline: none;
        background: rgba(255,255,255,0.15);
        border-color: #4fc3f7;
        box-shadow: 0 0 0 3px rgba(79, 195, 247, 0.15);
    }}
    .controls-vertical select option {{
        background: #1a1a2e;
        color: #ffffff;
    }}
    
    .controls-vertical button {{
        width: 100%;
        padding: 12px 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 8px;
    }}
    .controls-vertical button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }}
    
    .stats-box {{
        background: rgba(255,255,255,0.05);
        padding: 14px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 13px;
        line-height: 1.8;
    }}
    .stats-box div {{
        margin: 6px 0;
        display: flex;
        justify-content: space-between;
    }}
    .stats-box strong {{
        color: #4fc3f7;
    }}
    
    .path-info {{
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(56, 142, 60, 0.15) 100%);
        border: 1px solid rgba(76, 175, 80, 0.4);
        padding: 14px;
        border-radius: 12px;
        margin-top: 12px;
        font-size: 13px;
        display: none;
    }}
    .path-info.show {{
        display: block;
    }}
    .path-info-title {{
        font-weight: 700;
        margin-bottom: 10px;
        color: #66bb6a;
    }}
    
    .loading {{
        display: none;
        text-align: center;
        padding: 12px;
        font-size: 13px;
        color: #4fc3f7;
        background: rgba(79, 195, 247, 0.1);
        border-radius: 8px;
        margin: 8px 0;
    }}
    .loading.show {{
        display: block;
    }}
    
    .zoom-controls {{
        display: flex;
        gap: 8px;
        margin-top: 8px;
    }}
    .zoom-controls button {{
        flex: 1;
        padding: 10px;
        font-size: 14px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }}
    
    .legend-box {{
        background: rgba(255,255,255,0.05);
        padding: 12px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 12px;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        margin: 6px 0;
    }}
    .legend-color {{
        width: 20px;
        height: 20px;
        border-radius: 4px;
        margin-right: 10px;
        border: 1px solid rgba(255,255,255,0.3);
    }}
    .heatmap-toggle {{
        margin-top: 12px;
    }}
</style>

<div class="controls-box">
    <div class="controls-vertical">
        <div class="section-title">Estatísticas</div>
        <div class="stats-box">
            <div><strong>Lutadores:</strong> {total_lutadores}</div>
            <div><strong>Lutas:</strong> {total_lutas}</div>
            <div><strong>Densidade:</strong> {densidade_media:.4f}</div>
        </div>
        
        <div class="section-title">Busca</div>
        <input type="text" id="busca-lutador" placeholder="Digite o nome do lutador..." onkeypress="if(event.key==='Enter') buscarLutador()">
        <div style="display: flex; gap: 4px;">
            <button onclick="buscarLutador()" style="flex: 1;">Buscar</button>
            <button onclick="limparBusca()" style="flex: 1;">Limpar</button>
        </div>
        
        <div class="section-title">Caminhos</div>
        <select id="origem-select">
            <option value="">Selecione a origem...</option>
{lutadores_options}
        </select>
        <select id="destino-select">
            <option value="">Selecione o destino...</option>
{lutadores_options}
        </select>
        <div class="loading" id="loading-indicator">Calculando caminho...</div>
        <button onclick="calcularCaminho()">Calcular Caminho</button>
        <button onclick="resetHighlight()">Limpar Destaques</button>
        <div class="path-info" id="path-info">
            <div class="path-info-title">Informações do Caminho</div>
            <div class="path-info-content" id="path-info-content"></div>
        </div>
        
        <div class="section-title">Heatmap de Vitórias</div>
        <div class="legend-box">
            <div class="legend-item">
                <span class="legend-color" style="background-color: #e0e0e0"></span>
                <span>0 vitórias</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #90caf9"></span>
                <span>1-2 vitórias</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #42a5f5"></span>
                <span>3-5 vitórias</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #1976d2"></span>
                <span>6-10 vitórias</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #0d47a1"></span>
                <span>10+ vitórias</span>
            </div>
            <div class="heatmap-toggle">
                <button onclick="toggleHeatmap()" id="heatmap-btn">Desativar Heatmap</button>
            </div>
        </div>
        
        <div class="section-title">Zoom</div>
        <div class="zoom-controls">
            <button onclick="zoomIn()">➕</button>
            <button onclick="zoomOut()">➖</button>
            <button onclick="resetView()">Reverter</button>
        </div>
        
        <div class="section-title">Performance</div>
        <button onclick="togglePhysics()" id="physics-btn">Desativar Física</button>
        <div style="font-size: 11px; color: rgba(255,255,255,0.6); margin-top: 8px; line-height: 1.4;">
            Desative a física após a estabilização para melhorar a performance.
        </div>
    </div>
</div>
"""

    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + controls_html, 1)

    graph_data_js = json.dumps(graph_data, ensure_ascii=False)

    extra_js = """
<script type="text/javascript">
    var graphData = """ + graph_data_js + """;
    var vitoriasMap = """ + vitorias_map_js + """;
    var heatmapEnabled = true;
    
    network.on("click", function(params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            var node = nodes.get(nodeId);
            if (node && node.title) {
                console.log(node.title);
            }
        }
    });
    
    function buscarLutador() {
        var input = document.getElementById('busca-lutador');
        if (!input) return;
        var nome = input.value.trim();
        if (!nome) return;

        if (typeof nodes === 'undefined') {
            alert('Grafo ainda não foi carregado.');
            return;
        }

        var allNodes = nodes.get();
        var nomeLower = nome.toLowerCase();
        var found = null;
        var matches = [];

        for (var i = 0; i < allNodes.length; i++) {
            var n = allNodes[i];
            if (n.id === nome || (n.label && n.label.toLowerCase() === nomeLower)) {
                found = n;
                break;
            }
            if (n.label && n.label.toLowerCase().includes(nomeLower)) {
                matches.push(n);
            }
        }

        if (!found) {
            if (matches.length === 0) {
                alert("Lutador não encontrado: " + nome);
                return;
            } else if (matches.length === 1) {
                found = matches[0];
            } else {
                var matchIds = matches.map(function(n) { return n.id; });
                network.selectNodes(matchIds);
                network.fit({
                    nodes: matchIds,
                    animation: { duration: 800 }
                });
                return;
            }
        }

        network.selectNodes([found.id]);
        network.focus(found.id, {
            scale: 1.6,
            animation: { duration: 800 }
        });
    }
    
    function limparBusca() {
        var input = document.getElementById('busca-lutador');
        if (input) input.value = '';
        network.unselectAll();
        network.fit({ animation: { duration: 600 } });
    }
    
    function showPathInfo(path, distance) {
        var pathInfo = document.getElementById('path-info');
        var pathInfoContent = document.getElementById('path-info-content');
        if (!pathInfo || !pathInfoContent) return;
        
        var steps = path.length - 1;
        var pathList = path.join(' → ');
        
        pathInfoContent.innerHTML = 
            '<div><strong>Distância:</strong> ' + distance + ' conexões</div>' +
            '<div><strong>Passos:</strong> ' + steps + '</div>' +
            '<div style="margin-top: 6px; font-size: 11px; max-height: 100px; overflow-y: auto;">' +
            '<strong>Rota:</strong><br>' + pathList +
            '</div>';
        
        pathInfo.classList.add('show');
    }
    
    function hidePathInfo() {
        var pathInfo = document.getElementById('path-info');
        if (pathInfo) pathInfo.classList.remove('show');
    }
    
    function showLoading() {
        var loading = document.getElementById('loading-indicator');
        if (loading) loading.classList.add('show');
    }
    
    function hideLoading() {
        var loading = document.getElementById('loading-indicator');
        if (loading) loading.classList.remove('show');
    }
    
    function zoomIn() {
        var scale = network.getScale();
        network.moveTo({ scale: Math.min(scale * 1.3, 5), animation: { duration: 300 } });
    }
    
    function zoomOut() {
        var scale = network.getScale();
        network.moveTo({ scale: Math.max(scale / 1.3, 0.1), animation: { duration: 300 } });
    }
    
    function resetView() {
        network.fit({ animation: { duration: 800 } });
    }
    
    function calcularCaminho() {
        var origemSelect = document.getElementById('origem-select');
        var destinoSelect = document.getElementById('destino-select');
        
        if (!origemSelect || !destinoSelect) return;
        
        var origem = origemSelect.value;
        var destino = destinoSelect.value;
        
        if (!origem || !destino) {
            alert('Selecione origem e destino');
            return;
        }
        
        showLoading();
        resetHighlight();
        
        setTimeout(function() {
            calcularCaminhoBFS(origem, destino);
            hideLoading();
        }, 50);
    }
    
    function calcularCaminhoBFS(origem, destino) {
        var adjMap = {};
        
        for (var lutador in graphData) {
            if (!adjMap[lutador]) adjMap[lutador] = [];
            for (var oponente in graphData[lutador]) {
                adjMap[lutador].push(oponente);
            }
        }
        
        var dist = {};
        var parent = {};
        var queue = [origem];
        
        dist[origem] = 0;
        parent[origem] = null;
        
        var found = false;
        while (queue.length > 0 && !found) {
            var current = queue.shift();
            
            if (current === destino) {
                found = true;
                break;
            }
            
            var neighbors = adjMap[current] || [];
            for (var k = 0; k < neighbors.length; k++) {
                var neighbor = neighbors[k];
                
                if (dist[neighbor] === undefined) {
                    dist[neighbor] = dist[current] + 1;
                    parent[neighbor] = current;
                    queue.push(neighbor);
                }
            }
        }
        
        if (dist[destino] === undefined) {
            alert('Não foi encontrado um caminho entre ' + origem + ' e ' + destino);
            return;
        }
        
        var path = [];
        var current = destino;
        while (current !== null) {
            path.unshift(current);
            current = parent[current];
        }
        
        destacarCaminho(path, dist[destino]);
        showPathInfo(path, dist[destino]);
    }
    
    function destacarCaminho(path, distancia) {
        if (typeof nodes === 'undefined' || typeof edges === 'undefined') return;
        
        resetHighlightColors();
        
        var pathEdgeSet = {};
        for (var k = 0; k < path.length - 1; k++) {
            var key = [path[k], path[k+1]].sort().join("||");
            pathEdgeSet[key] = true;
        }
        
        var allEdges = edges.get();
        var allNodes = nodes.get();
        
        for (var i = 0; i < allEdges.length; i++) {
            var e = allEdges[i];
            var key = [e.from, e.to].sort().join("||");
            if (pathEdgeSet[key]) {
                if (e._originalColor === undefined) e._originalColor = e.color;
                if (e._originalWidth === undefined) e._originalWidth = e.width;
                e.color = { color: '#FF6B6B' };
                e.width = 10;
            } else {
                if (e._originalColor === undefined) e._originalColor = e.color;
                if (e._originalWidth === undefined) e._originalWidth = e.width;
                e.color = { color: '#e6e6e6' };
                e.width = 0.5;
            }
        }
        edges.update(allEdges);
        
        for (var i = 0; i < allNodes.length; i++) {
            var n = allNodes[i];
            if (path.indexOf(n.id) !== -1) {
                if (n._originalColor === undefined) n._originalColor = n.color;
                n.color = { background: '#FF6B6B', border: '#C92A2A' };
            }
        }
        nodes.update(allNodes);
        
        setTimeout(function() {
            network.fit({ nodes: path, animation: { duration: 800 } });
        }, 100);
    }
    
    function resetHighlightColors() {
        if (typeof nodes === 'undefined' || typeof edges === 'undefined') return;
        
        var allEdges = edges.get();
        for (var i = 0; i < allEdges.length; i++) {
            var e = allEdges[i];
            if (e._originalColor !== undefined) {
                e.color = e._originalColor;
            }
            if (e._originalWidth !== undefined) {
                e.width = e._originalWidth;
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
        resetHighlightColors();
        hidePathInfo();
        network.fit({ animation: { duration: 800 } });
    }
    
    function getColorByVitorias(vitorias) {
        if (vitorias === 0) return '#e0e0e0';
        if (vitorias <= 2) return '#90caf9';
        if (vitorias <= 5) return '#42a5f5';
        if (vitorias <= 10) return '#1976d2';
        return '#0d47a1';
    }
    
    function toggleHeatmap() {
        if (typeof nodes === 'undefined') return;
        
        heatmapEnabled = !heatmapEnabled;
        var btn = document.getElementById('heatmap-btn');
        
        if (btn) {
            btn.textContent = heatmapEnabled ? 'Desativar Heatmap' : 'Ativar Heatmap';
        }
        
        var allNodes = nodes.get();
        var defaultColor = '#d3d3d3';
        
        for (var i = 0; i < allNodes.length; i++) {
            var n = allNodes[i];
            var lutadorId = n.id;
            var vitorias = vitoriasMap[lutadorId] || 0;
            
            if (heatmapEnabled) {
                var cor = getColorByVitorias(vitorias);
                n.color = { background: cor, border: '#222222' };
            } else {
                n.color = { background: defaultColor, border: '#222222' };
            }
            
            if (n._originalColor !== undefined) {
                n._originalColor = n.color;
            }
        }
        
        nodes.update(allNodes);
    }
    
    var physicsEnabled = true;
    
    function togglePhysics() {
        physicsEnabled = !physicsEnabled;
        var btn = document.getElementById('physics-btn');
        
        if (btn) {
            btn.textContent = physicsEnabled ? 'Desativar Física' : 'Ativar Física';
        }
        
        network.setOptions({
            physics: {
                enabled: physicsEnabled
            }
        });
        
        if (!physicsEnabled) {
            console.log('Física desativada - grafo está estático para melhor performance');
        } else {
            console.log('Física ativada - grafo irá se reorganizar');
        }
    }
    
    network.once('stabilizationIterationsDone', function() {
        console.log('Grafo estabilizado!');
        setTimeout(function() {
            if (physicsEnabled) {
                togglePhysics();
                console.log('Física desativada automaticamente para melhor performance');
            }
        }, 2000);
    });
</script>
"""

    if "</body>" in html:
        html = html.replace("</body>", extra_js + "\n</body>", 1)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)

def gerar_histograma_graus():
    """Gera histograma da distribuição de graus dos lutadores do UFC."""
    os.makedirs(OUT_DIR, exist_ok=True)

    caminho_ufc = os.path.join(DATA_DIR, "total_fight_data_processado.csv")
    grafo = carregar_grafo_ufc(caminho_ufc)
    lutadores = grafo.obter_nos()

    graus = []
    for lutador in lutadores:
        grau = grafo.grau(lutador)
        graus.append({'lutador': lutador, 'grau': grau})
    
    df_graus = pd.DataFrame(graus)

    caminho_csv = os.path.join(OUT_DIR, 'graus_lutadores.csv')
    df_graus.to_csv(caminho_csv, index=False)
    print(f"Dados de graus salvos em: {caminho_csv}")

    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")

    ax = sns.histplot(data=df_graus, x='grau', bins=30, kde=True, color='#667eea')

    plt.title('Distribuição dos Graus dos Lutadores do UFC', fontsize=16, pad=20, fontweight='bold')
    plt.xlabel('Grau do Vértice (Número de Lutas)', fontsize=12)
    plt.ylabel('Frequência', fontsize=12)

    plt.grid(True, linestyle='--', alpha=0.7)

    media = df_graus['grau'].mean()
    mediana = df_graus['grau'].median()
    plt.axvline(media, color='red', linestyle='--', linewidth=2, label=f'Média: {media:.1f}')
    plt.axvline(mediana, color='green', linestyle='--', linewidth=2, label=f'Mediana: {mediana:.1f}')
    plt.legend()

    plt.tight_layout()

    caminho_saida = os.path.join(OUT_DIR, 'distribuicao_graus.png')
    plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Histograma de distribuição de graus salvo em: {caminho_saida}")
    print(f"Estatísticas: Média = {media:.2f}, Mediana = {mediana:.2f}, Min = {df_graus['grau'].min()}, Max = {df_graus['grau'].max()}")

if __name__ == "__main__":
    grafo_interativo_ufc_html()
    gerar_histograma_graus()
