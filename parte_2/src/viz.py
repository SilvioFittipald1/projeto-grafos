import os
import json
import time
import tracemalloc
import pandas as pd
import webbrowser
from collections import deque
from pyvis.network import Network
from .graphs.io import carregar_grafo_ufc
from .graphs.algorithms import bfs_arvore, dfs_arvore, dfs_detectar_ciclo, dfs_classificar_arestas, dijkstra, bellman_ford, bellman_ford_caminho
from .graphs.graph import Graph
from math import inf
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out")
OUT_HTML_DIR = os.path.join(BASE_DIR, "out")
REPORT_PATH = os.path.join(OUT_DIR, "parte2_report.json")

def grafo_interativo_ufc_html():
    if Network is None:
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    caminho_ufc = os.path.join(DATA_DIR, "total_fight_data_processado.csv")
    grafo = carregar_grafo_ufc(caminho_ufc)
    lutadores = grafo.obter_nos()
    todas_vitorias = grafo.obter_todas_vitorias()
    total_lutadores = grafo.ordem()
    total_lutas = grafo.tamanho()
    densidade_media = grafo.densidade()
    
    df = pd.read_csv(caminho_ufc, sep=';', encoding='utf-8')
    fight_types_map = {}
    for _, row in df.iterrows():
        r_fighter = row['R_fighter']
        b_fighter = row['B_fighter']
        fight_type = str(row['Fight_type']).replace(' Bout', '').replace(' Title', '').replace('UFC ', '').strip()
        key = tuple(sorted([r_fighter, b_fighter]))
        fight_types_map[key] = fight_type
    
    categorias_unicas = sorted(set(fight_types_map.values()))
    categorias_principais = [c for c in categorias_unicas if any(peso in c for peso in ['Lightweight', 'Welterweight', 'Middleweight', 'Light Heavyweight', 'Heavyweight', 'Featherweight', 'Bantamweight', 'Flyweight'])]

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
    fight_types_map_js = json.dumps({f"{k[0]}||{k[1]}": v for k, v in fight_types_map.items()}, ensure_ascii=False)
    categorias_principais_js = json.dumps(categorias_principais, ensure_ascii=False)

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
        
        <div class="section-title">Categorias de Peso</div>
        <select id="categoria-select" onchange="destacarCategoria()">
            <option value="">Selecione uma categoria...</option>
            <option value="Lightweight">Lightweight</option>
            <option value="Welterweight">Welterweight</option>
            <option value="Middleweight">Middleweight</option>
            <option value="Light Heavyweight">Light Heavyweight</option>
            <option value="Heavyweight">Heavyweight</option>
            <option value="Featherweight">Featherweight</option>
            <option value="Bantamweight">Bantamweight</option>
            <option value="Flyweight">Flyweight</option>
            <option value="Strawweight">Strawweight</option>
        </select>
        <button onclick="limparCategoria()">Limpar Categoria</button>
        
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
    var fightTypesMap = """ + fight_types_map_js + """;
    var heatmapEnabled = true;
    var categoriaAtiva = null;
    
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
    
    function destacarCategoria() {
        var select = document.getElementById('categoria-select');
        if (!select) return;
        
        var categoria = select.value;
        
        if (!categoria) {
            limparCategoria();
            return;
        }
        
        if (typeof nodes === 'undefined' || typeof edges === 'undefined') return;
        
        categoriaAtiva = categoria;
        
        var allEdges = edges.get();
        var allNodes = nodes.get();
        var nodosDestacados = new Set();
        
        for (var i = 0; i < allEdges.length; i++) {
            var e = allEdges[i];
            var key = [e.from, e.to].sort().join("||");
            var fightType = fightTypesMap[key] || "";
            
            if (fightType.includes(categoria)) {
                if (e._originalColor === undefined) e._originalColor = e.color;
                if (e._originalWidth === undefined) e._originalWidth = e.width;
                e.color = { color: '#FF6B6B' };
                e.width = 3;
                nodosDestacados.add(e.from);
                nodosDestacados.add(e.to);
            } else {
                if (e._originalColor === undefined) e._originalColor = e.color;
                if (e._originalWidth === undefined) e._originalWidth = e.width;
                e.color = { color: '#e6e6e6', opacity: 0.2 };
                e.width = 0.3;
            }
        }
        edges.update(allEdges);
        
        for (var i = 0; i < allNodes.length; i++) {
            var n = allNodes[i];
            if (nodosDestacados.has(n.id)) {
                if (n._originalColor === undefined) n._originalColor = n.color;
                n.color = { background: '#FF6B6B', border: '#C92A2A' };
            } else {
                if (n._originalColor === undefined) n._originalColor = n.color;
                n.color = { background: '#e0e0e0', border: '#999999' };
            }
        }
        nodes.update(allNodes);
    }
    
    function limparCategoria() {
        var select = document.getElementById('categoria-select');
        if (select) select.value = '';
        
        categoriaAtiva = null;
        
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
    

def registrar_metricas(algorithm: str, task: str, time_ms: float, memory_kb: float = None,
                       dataset: str = "total_fight_data_processado.csv"):
    os.makedirs(OUT_DIR, exist_ok=True)
    
    data = {"runs": []}
    if os.path.exists(REPORT_PATH):
        try:
            with open(REPORT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"runs": []}
    
    registro = {
        "algorithm": algorithm,
        "task": task,
        "dataset": dataset,
        "time_ms": float(time_ms),
    }
    if memory_kb is not None:
        registro["memory_kb"] = float(memory_kb)
    
    data["runs"].append(registro)
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def medir_e_registrar(algorithm: str, task: str, func, *args, medir_memoria: bool = True, **kwargs):
    dataset = "total_fight_data_processado.csv"
    
    if medir_memoria:
        tracemalloc.start()
    
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    
    time_ms = (end - start) * 1000.0
    
    memory_kb = None
    if medir_memoria:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory_kb = peak / 1024.0
    
    registrar_metricas(algorithm, task, time_ms, memory_kb, dataset=dataset)
    return result


def carregar_grafo_parte2():
    caminho_ufc = os.path.join(DATA_DIR, "total_fight_data_processado.csv")
    return carregar_grafo_ufc(caminho_ufc)


def _obter_vertices_mais_conectados(grafo: Graph, n: int = 3):
    vertices_com_grau = [(v, grafo.grau(v)) for v in grafo.obter_nos()]
    vertices_com_grau.sort(key=lambda x: x[1], reverse=True)
    return [v for v, _ in vertices_com_grau[:n]]


def _detectar_ciclos_bfs(grafo: Graph, origem: str, pai: dict, nivel: dict):
    vertices_alcancados = set(pai.keys())
    for u in vertices_alcancados:
        for v, _ in grafo.vizinhos(u):
            if v in vertices_alcancados:
                if pai.get(u) != v and pai.get(v) != u:
                    return True
    return False


def gerar_html_bfs(out_path: str = None):
    if out_path is None:
        os.makedirs(OUT_HTML_DIR, exist_ok=True)
        out_path = os.path.join(OUT_HTML_DIR, "parte2_bfs.html")
    else:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    grafo = carregar_grafo_parte2()
    origens = _obter_vertices_mais_conectados(grafo, 3)
    
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualização BFS - Parte 2</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 40px;
            padding: 10px;
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .resumo {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .ciclo-detectado {
            color: #d32f2f;
            font-weight: bold;
        }
        .sem-ciclo {
            color: #388e3c;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Visualização do Algoritmo BFS (Breadth-First Search)</h1>
""")
    
    for origem in origens:
        pai, nivel = medir_e_registrar(
            algorithm="BFS",
            task=f"BFS a partir de {origem}",
            func=bfs_arvore,
            grafo=grafo,
            origem=origem
        )
        
        vertices_ordenados = []
        ordem_visita = {}
        contador = 0
        fila = [origem]
        visitado_ordem = {origem: contador}
        contador += 1
        
        while fila:
            atual = fila.pop(0)
            for vizinho, _ in grafo.vizinhos(atual):
                if vizinho in pai and pai[vizinho] == atual and vizinho not in visitado_ordem:
                    visitado_ordem[vizinho] = contador
                    contador += 1
                    fila.append(vizinho)
        
        vertices_info = []
        for v in pai.keys():
            vertices_info.append({
                'vertice': v,
                'nivel': nivel[v],
                'ordem': visitado_ordem.get(v, -1)
            })
        
        vertices_info.sort(key=lambda x: (x['nivel'], x['ordem']))
        tem_ciclo = _detectar_ciclos_bfs(grafo, origem, pai, nivel)
        
        html_parts.append(f"""
    <h2>BFS a partir de {origem}</h2>
    <table>
        <thead>
            <tr>
                <th>Vértice</th>
                <th>Nível</th>
                <th>Ordem de Visita</th>
            </tr>
        </thead>
        <tbody>
""")
        
        for info in vertices_info:
            html_parts.append(f"""
            <tr>
                <td>{info['vertice']}</td>
                <td>{info['nivel']}</td>
                <td>{info['ordem']}</td>
            </tr>
""")
        
        html_parts.append("""        </tbody>
    </table>
    <div class="resumo">
""")
        
        if tem_ciclo:
            html_parts.append(f"""
        <p><span class="ciclo-detectado">Ciclos detectados:</span> Sim, foram detectados ciclos na componente alcançada a partir de {origem}.</p>
""")
        else:
            html_parts.append(f"""
        <p><span class="sem-ciclo">Ciclos detectados:</span> Não, não foram detectados ciclos na componente alcançada a partir de {origem}.</p>
""")
        
        html_parts.append(f"""
        <p><strong>Total de vértices alcançados:</strong> {len(pai)}</p>
        <p><strong>Nível máximo:</strong> {max(nivel.values()) if nivel else 0}</p>
    </div>
""")
    
    html_parts.append("""
</body>
</html>
""")
    
    html_content = "".join(html_parts)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    abs_path = os.path.abspath(out_path)
    if os.name == 'nt':
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
    else:
        file_url = f"file://{abs_path}"
    webbrowser.open(file_url)
    
    return out_path


def gerar_html_dfs(out_path: str = None):
    if out_path is None:
        os.makedirs(OUT_HTML_DIR, exist_ok=True)
        out_path = os.path.join(OUT_HTML_DIR, "parte2_dfs.html")
    else:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    grafo = carregar_grafo_parte2()
    origens = _obter_vertices_mais_conectados(grafo, 3)
    
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualização DFS - Parte 2</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            border-bottom: 3px solid #f5576c;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 40px;
            padding: 10px;
            background-color: #fce4ec;
            border-left: 4px solid #e91e63;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f5576c;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .resumo {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .ciclo-detectado {
            color: #d32f2f;
            font-weight: bold;
        }
        .sem-ciclo {
            color: #388e3c;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Visualização do Algoritmo DFS (Depth-First Search)</h1>
""")
    
    for origem in origens:
        pai, descoberta = medir_e_registrar(
            algorithm="DFS",
            task=f"DFS a partir de {origem}",
            func=dfs_arvore,
            grafo=grafo,
            origem=origem
        )
        
        def calcular_profundidade(vertice, pai_dict, origem):
            if vertice == origem:
                return 0
            if vertice not in pai_dict or pai_dict[vertice] is None:
                return 0
            
            cache_profundidade = {origem: 0}
            
            def calcular_recursivo(v):
                if v in cache_profundidade:
                    return cache_profundidade[v]
                if v not in pai_dict or pai_dict[v] is None:
                    return 0
                pai_v = pai_dict[v]
                if pai_v == origem:
                    cache_profundidade[v] = 1
                    return 1
                prof_pai = calcular_recursivo(pai_v)
                cache_profundidade[v] = prof_pai + 1
                return prof_pai + 1
            
            return calcular_recursivo(vertice)
        
        vertices_info = []
        for v in pai.keys():
            profundidade = calcular_profundidade(v, pai, origem)
            vertices_info.append({
                'vertice': v,
                'ordem': descoberta.get(v, -1),
                'profundidade': profundidade
            })
        
        vertices_info.sort(key=lambda x: x['ordem'])
        classificacao_arestas = medir_e_registrar(
            algorithm="DFS",
            task=f"DFS edge classification a partir de {origem}",
            func=dfs_classificar_arestas,
            grafo=grafo,
            medir_memoria=False
        )
        tem_ciclo = any(tipo == "back" for tipo in classificacao_arestas.values())
        
        html_parts.append(f"""
    <h2>DFS a partir de {origem}</h2>
    <table>
        <thead>
            <tr>
                <th>Vértice</th>
                <th>Nível</th>
                <th>Ordem de Visita</th>
            </tr>
        </thead>
        <tbody>
""")
        
        for info in vertices_info:
            html_parts.append(f"""
            <tr>
                <td>{info['vertice']}</td>
                <td>{info['profundidade']}</td>
                <td>{info['ordem']}</td>
            </tr>
""")
        
        html_parts.append("""        </tbody>
    </table>
    <div class="resumo">
""")
        
        if tem_ciclo:
            html_parts.append(f"""
        <p><span class="ciclo-detectado">Ciclos detectados:</span> Sim, foram encontrados ciclos na travessia em profundidade a partir de {origem} (arestas de retorno detectadas).</p>
""")
        else:
            html_parts.append(f"""
        <p><span class="sem-ciclo">Ciclos detectados:</span> Não, não foram encontrados ciclos na travessia em profundidade a partir de {origem}.</p>
""")
        
        profundidade_max = max([info['profundidade'] for info in vertices_info]) if vertices_info else 0
        html_parts.append(f"""
        <p><strong>Total de vértices alcançados:</strong> {len(pai)}</p>
        <p><strong>Profundidade máxima:</strong> {profundidade_max}</p>
    </div>
""")
    
    html_parts.append("""
</body>
</html>
""")
    
    html_content = "".join(html_parts)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    abs_path = os.path.abspath(out_path)
    if os.name == 'nt':
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
    else:
        file_url = f"file://{abs_path}"
    webbrowser.open(file_url)
    
    return out_path


def gerar_html_dijkstra(out_path: str = None):
    if out_path is None:
        os.makedirs(OUT_HTML_DIR, exist_ok=True)
        out_path = os.path.join(OUT_HTML_DIR, "parte2_dijkstra.html")
    else:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    grafo = carregar_grafo_parte2()
    vertices_conectados = _obter_vertices_mais_conectados(grafo, 10)
    
    pares = []
    for i in range(min(5, len(vertices_conectados))):
        origem = vertices_conectados[i]
        destino = None
        for j in range(i + 1, len(vertices_conectados)):
            candidato = vertices_conectados[j]
            visitado = set()
            fila = deque([origem])
            visitado.add(origem)
            encontrou = False
            
            while fila:
                atual = fila.popleft()
                if atual == candidato:
                    encontrou = True
                    break
                for vizinho, _ in grafo.vizinhos(atual):
                    if vizinho not in visitado:
                        visitado.add(vizinho)
                        fila.append(vizinho)
            
            if encontrou:
                destino = candidato
                break
        
        if destino:
            pares.append((origem, destino))
    
    if len(pares) < 5:
        todos_vertices = grafo.obter_nos()
        for origem in vertices_conectados[:5]:
            if len(pares) >= 5:
                break
            for destino in todos_vertices:
                if origem != destino and (origem, destino) not in pares and (destino, origem) not in pares:
                    visitado = set()
                    fila = deque([origem])
                    visitado.add(origem)
                    encontrou = False
                    
                    while fila:
                        atual = fila.popleft()
                        if atual == destino:
                            encontrou = True
                            break
                        for vizinho, _ in grafo.vizinhos(atual):
                            if vizinho not in visitado:
                                visitado.add(vizinho)
                                fila.append(vizinho)
                    
                    if encontrou:
                        pares.append((origem, destino))
                        break
    
    pares = pares[:5]
    
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualização Dijkstra - Parte 2</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            border-bottom: 3px solid #4caf50;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #4caf50;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .caminho {
            font-family: 'Courier New', monospace;
            color: #1976d2;
        }
        .explicacao {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>Visualização do Algoritmo Dijkstra</h1>
    <table>
        <thead>
            <tr>
                <th>Origem</th>
                <th>Destino</th>
                <th>Caminho</th>
                <th>Distância Total</th>
            </tr>
        </thead>
        <tbody>
""")
    
    for origem, destino in pares:
        distancia, caminho = medir_e_registrar(
            algorithm="DIJKSTRA",
            task=f"DIJKSTRA {origem} -> {destino}",
            func=dijkstra,
            grafo=grafo,
            origem=origem,
            destino=destino
        )
        
        if distancia == inf or not caminho:
            caminho_str = "Sem caminho"
            distancia_str = "∞"
        else:
            caminho_str = " → ".join(caminho)
            distancia_str = f"{distancia:.2f}"
        
        html_parts.append(f"""
            <tr>
                <td>{origem}</td>
                <td>{destino}</td>
                <td class="caminho">{caminho_str}</td>
                <td>{distancia_str}</td>
            </tr>
""")
    
    html_parts.append("""        </tbody>
    </table>
    <div class="explicacao">
        <h3>Explicação</h3>
        <p>A distância total representa a soma dos pesos das arestas no caminho mínimo entre origem e destino.</p>
        <p>No contexto deste grafo de lutadores do UFC, os pesos das arestas indicam a importância/tipo da vitória:</p>
        <ul>
            <li>Nocaute/Submissão: peso 0.5</li>
            <li>Decisão Unânime: peso 2.0</li>
            <li>Decisão Dividida/Majoritária: peso 3.0</li>
            <li>Outros: peso 1.0</li>
        </ul>
        <p>O algoritmo Dijkstra encontra o caminho com menor soma de pesos entre dois lutadores.</p>
    </div>
</body>
</html>
""")
    
    html_content = "".join(html_parts)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    abs_path = os.path.abspath(out_path)
    if os.name == 'nt':
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
    else:
        file_url = f"file://{abs_path}"
    webbrowser.open(file_url)
    
    return out_path


def gerar_html_bellman_ford(out_path: str = None):
    if out_path is None:
        os.makedirs(OUT_HTML_DIR, exist_ok=True)
        out_path = os.path.join(OUT_HTML_DIR, "parte2_bellman_ford.html")
    else:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualização Bellman-Ford - Parte 2</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            border-bottom: 3px solid #ff9800;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 40px;
            padding: 10px;
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #ff9800;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .resumo {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .ciclo-negativo {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            color: #c62828;
            font-weight: bold;
        }
        .sem-ciclo {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            color: #2e7d32;
        }
    </style>
</head>
<body>
    <h1>Visualização do Algoritmo Bellman-Ford</h1>
""")
    
    grafo_sem_ciclo = Graph()
    grafo_sem_ciclo.adicionar_aresta("A", "B", 1.0)
    grafo_sem_ciclo.adicionar_aresta("A", "C", 4.0)
    grafo_sem_ciclo.adicionar_aresta("B", "C", -2.0)
    grafo_sem_ciclo.adicionar_aresta("B", "D", 3.0)
    grafo_sem_ciclo.adicionar_aresta("C", "D", 2.0)
    grafo_sem_ciclo.adicionar_aresta("D", "E", -1.0)
    
    origem_caso1 = "A"
    dist, anterior, tem_ciclo = medir_e_registrar(
        algorithm="BELLMAN_FORD",
        task="BF case1: neg weights, no neg cycle (expected)",
        func=bellman_ford,
        grafo=grafo_sem_ciclo,
        origem=origem_caso1
    )
    
    html_parts.append(f"""
    <h2>Caso 1: Grafo com Pesos Negativos (Sem Ciclo Negativo)</h2>
    <p><strong>Origem:</strong> {origem_caso1}</p>
    <p><strong>Estrutura do grafo:</strong></p>
    <ul>
        <li>A → B (peso 1.0)</li>
        <li>A → C (peso 4.0)</li>
        <li>B → C (peso -2.0) <strong>Peso negativo</strong></li>
        <li>B → D (peso 3.0)</li>
        <li>C → D (peso 2.0)</li>
        <li>D → E (peso -1.0) <strong>Peso negativo</strong></li>
    </ul>
    <p><strong>Análise:</strong> Este grafo contém arestas com pesos negativos, mas não possui ciclos negativos. 
    Todos os ciclos possíveis têm soma de pesos positiva ou zero.</p>
    <table>
        <thead>
            <tr>
                <th>Vértice</th>
                <th>Distância</th>
                <th>Predecessor</th>
            </tr>
        </thead>
        <tbody>
""")
    
    for vertice in sorted(dist.keys()):
        distancia_val = dist[vertice]
        pred = anterior[vertice]
        distancia_str = f"{distancia_val:.2f}" if distancia_val != inf else "∞"
        pred_str = pred if pred else "-"
        
        html_parts.append(f"""
            <tr>
                <td>{vertice}</td>
                <td>{distancia_str}</td>
                <td>{pred_str}</td>
            </tr>
""")
    
    html_parts.append("""        </tbody>
    </table>
""")
    
    if tem_ciclo:
        html_parts.append("""
    <div class="ciclo-negativo">
        <p>Ciclo negativo detectado!</p>
    </div>
""")
    else:
        html_parts.append("""
    <div class="sem-ciclo">
        <p>Nao foi detectado ciclo negativo.</p>
    </div>
""")
    
    grafo_com_ciclo = Graph()
    grafo_com_ciclo.adicionar_aresta("X", "Y", 1.0)
    grafo_com_ciclo.adicionar_aresta("Y", "Z", 2.0)
    grafo_com_ciclo.adicionar_aresta("Z", "X", -5.0)
    
    origem_caso2 = "X"
    dist2, anterior2, tem_ciclo2 = medir_e_registrar(
        algorithm="BELLMAN_FORD",
        task="BF case2: negative cycle",
        func=bellman_ford,
        grafo=grafo_com_ciclo,
        origem=origem_caso2
    )
    
    html_parts.append(f"""
    <h2>Caso 2: Grafo com Ciclo Negativo (Detectado)</h2>
    <p><strong>Origem:</strong> {origem_caso2}</p>
    <p><strong>Estrutura do grafo:</strong></p>
    <ul>
        <li>X → Y (peso 1.0)</li>
        <li>Y → Z (peso 2.0)</li>
        <li>Z → X (peso -5.0) <strong>Peso negativo</strong></li>
    </ul>
    <p><strong>Ciclo negativo:</strong> X → Y → Z → X</p>
    <p><strong>Soma dos pesos do ciclo:</strong> 1.0 + 2.0 + (-5.0) = <strong>-2.0</strong> (negativo!)</p>
    <p><strong>Análise:</strong> Este grafo contém um ciclo com soma de pesos negativa. 
    O algoritmo Bellman-Ford deve detectar este ciclo negativo após |V|-1 iterações, 
    quando ainda é possível relaxar arestas.</p>
""")
    
    if tem_ciclo2:
        html_parts.append("""
    <div class="ciclo-negativo">
        <p><strong>Ciclo negativo detectado!</strong></p>
        <p>O algoritmo Bellman-Ford identificou a existência de um ciclo com soma de pesos negativa.</p>
        <p>Neste caso, as distâncias calculadas podem não ser confiáveis, pois é possível reduzir infinitamente o custo do caminho percorrendo o ciclo negativo repetidamente.</p>
    </div>
""")
    else:
        html_parts.append("""
    <div class="sem-ciclo">
        <p>Nao foi detectado ciclo negativo.</p>
    </div>
""")
    
    grafo_grande = carregar_grafo_parte2()
    origem_grande = _obter_vertices_mais_conectados(grafo_grande, 1)[0]
    dist3, anterior3, tem_ciclo3 = medir_e_registrar(
        algorithm="BELLMAN_FORD",
        task=f"BF case3: large graph from {origem_grande}",
        func=bellman_ford,
        grafo=grafo_grande,
        origem=origem_grande
    )
    vertices_ordenados = sorted(dist3.items(), key=lambda x: x[1] if x[1] != inf else float('inf'))
    vertices_amostra = vertices_ordenados[:20]
    
    html_parts.append(f"""
    <h2>Caso 3: Grafo Grande da Parte 2 (Pesos Positivos)</h2>
    <p><strong>Origem:</strong> {origem_grande}</p>
    <p><strong>Total de vértices no grafo:</strong> {grafo_grande.ordem()}</p>
    <p><em>Mostrando os 20 vértices mais próximos da origem:</em></p>
    <table>
        <thead>
            <tr>
                <th>Vértice</th>
                <th>Distância</th>
            </tr>
        </thead>
        <tbody>
""")
    
    for vertice, distancia_val in vertices_amostra:
        distancia_str = f"{distancia_val:.2f}" if distancia_val != inf else "∞"
        html_parts.append(f"""
            <tr>
                <td>{vertice}</td>
                <td>{distancia_str}</td>
            </tr>
""")
    
    html_parts.append("""        </tbody>
    </table>
""")
    
    if tem_ciclo3:
        html_parts.append("""
    <div class="ciclo-negativo">
        <p>Ciclo negativo detectado!</p>
    </div>
""")
    else:
        html_parts.append(f"""
    <div class="sem-ciclo">
        <p>Nao foi detectado ciclo negativo.</p>
        <p>O algoritmo Bellman-Ford funcionou corretamente no grafo grande com pesos positivos.</p>
        <p><strong>Vértices alcançáveis:</strong> {sum(1 for d in dist3.values() if d != inf)}</p>
    </div>
""")
    
    html_parts.append("""
</body>
</html>
""")
    
    html_content = "".join(html_parts)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    abs_path = os.path.abspath(out_path)
    if os.name == 'nt':
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
    else:
        file_url = f"file://{abs_path}"
    webbrowser.open(file_url)
    
    return out_path




if __name__ == "__main__":
    grafo_interativo_ufc_html()
    gerar_histograma_graus()
    gerar_html_bfs()
    gerar_html_dijkstra()
    gerar_html_bellman_ford()
    gerar_html_dfs()
