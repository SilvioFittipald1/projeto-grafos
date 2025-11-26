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

    Salva o resultado em out/arvore_percurso.html.
    """

    # 1) Carrega origem, destino e caminho a partir do JSON do PASSO 6
    origem, destino_rotulo, caminho = percurso_nova_descoberta_setubal(
        caminho_json
    )

    if caminho_saida is None:
        caminho_saida = os.path.join("out/parte1", "arvore_percurso.html")

    os.makedirs(OUT_DIR, exist_ok=True)

    # 2) Monta os rótulos dos nós
    labels = list(caminho)
    if destino_rotulo and len(labels) > 0:
        labels[-1] = destino_rotulo  # exibe "Boa Viagem (Setúbal)" no último nó

    # 3) Cria a rede pyvis (usar tamanhos e fontes consistentes com o grafo interativo)
    NODE_SIZE = 14
    FONT = {"size": 14, "face": "Arial", "strokeWidth": 0}

    net = Network(height="600px", width="100%", directed=False)
    net.barnes_hut()

    # garante fonte/legibilidade
    net.set_options('''{
      "nodes": { "font": { "size": 14, "face": "Arial" } },
      "edges": { "smooth": false },
      "physics": { "stabilization": { "enabled": true, "iterations": 800 } }
    }''')

    # Adiciona nós com tamanho uniforme; destaca origem e destino em rosa
    for i, label in enumerate(labels):
        titulo = label
        if i == 0:
            # origem (Nova Descoberta) em rosa forte
            color = {"background": "#ff66c4", "border": "#c0428f"}
        elif i == len(labels) - 1:
            # destino (Boa Viagem) em rosa
            color = {"background": "#ff66c4", "border": "#c0428f"}
        else:
            color = {"background": "#8ecae6", "border": "#2b7f9e"}

        net.add_node(label, label=label, title=titulo, color=color, size=NODE_SIZE, font=FONT)

    # Adiciona arestas entre nós consecutivos (largura uniforme)
    for i in range(len(labels) - 1):
        u = labels[i]
        v = labels[i + 1]
        net.add_edge(u, v, color="#dcdcdc", width=2)

    # 4) Gera o HTML
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



DATA_DIR = "parte1/data"
OUT_DIR = "out/parte1"


def mapa_graus_html():
    """
    Gera um HTML interativo (pyvis) onde:
    - cada nó é um bairro
    - a cor do nó varia com o grau (mais conexões = cor mais intensa)

    Usa o arquivo out/graus.csv já gerado no passo 4.

    Saída: out/mapa_graus.html
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

        legenda_html = f"""
<style>
  .gp-legend {{
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
  .gp-legend .bar {{
    height: 14px;
    border-radius: 8px;
    background: linear-gradient(90deg, {gradient_css});
    margin: 8px 0 6px 0;
  }}
  .gp-legend .ticks {{
    display:flex; justify-content:space-between; font-size:11px; color:#444; margin-top:4px;
  }}
</style>
<div class="gp-legend">
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
      - out/ego_bairro.csv  (densidade_ego por bairro)
      - data/bairros_unique.csv (bairro -> microrregiao)

    Calcula, para cada microrregiao, a média de densidade_ego
    e gera um gráfico de barras:

        out/ranking_densidade_ego_microrregiao.png
    """
    caminho_ego = os.path.join(OUT_DIR, "ego_bairro.csv")
    caminho_bairros = os.path.join(DATA_DIR, "bairros_unique.csv")

    if not os.path.exists(caminho_ego):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_ego}. "
            f"Certifique-se de ter gerado ego_bairro.csv antes."
        )

    if not os.path.exists(caminho_bairros):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_bairros}."
        )

    # 1) Lê ego_bairro.csv
    df_ego = pd.read_csv(caminho_ego)
    df_ego.columns = df_ego.columns.str.strip().str.lower()

    # Aqui esperamos algo como: bairro, grau, ordem_ego, tamanho_ego, densidade_ego
    if not {"bairro", "densidade_ego"}.issubset(df_ego.columns):
        raise ValueError(
            "ego_bairro.csv deve ter as colunas 'bairro' e 'densidade_ego'."
        )

    # 2) Lê bairros_unique.csv para obter a microrregiao de cada bairro
    df_bairros = pd.read_csv(caminho_bairros)
    df_bairros.columns = df_bairros.columns.str.strip().str.lower()

    if not {"bairro", "microrregiao"}.issubset(df_bairros.columns):
        raise ValueError(
            "bairros_unique.csv deve ter as colunas 'bairro' e 'microrregiao'."
        )

    # 3) Junta as informações pelo nome do bairro
    df_join = pd.merge(
        df_ego[["bairro", "densidade_ego"]],
        df_bairros[["bairro", "microrregiao"]],
        on="bairro",
        how="inner"
    )

    # 4) Agrupa por microrregiao e calcula a média da densidade_ego
    df_rank = (
        df_join
        .groupby("microrregiao", as_index=False)["densidade_ego"]
        .mean()
        .rename(columns={"densidade_ego": "densidade_ego_media"})
        .sort_values("densidade_ego_media", ascending=False)
    )

    # 5) Prepara dados para o gráfico de barras
    microrregioes = df_rank["microrregiao"].astype(str).tolist()
    densidades_medias = df_rank["densidade_ego_media"].tolist()

    if plt is None:
        print("matplotlib (plt) não está disponível, não dá pra gerar o PNG.")
        return

    # 6) Cria o gráfico de barras (estético e ordenado: microrregião 1..6)
    # Força a exibição das microrregiões 1..6 nesta ordem; se faltar, mostra 0.0
    ordem = [str(i) for i in range(1, 7)]

    # Normaliza as chaves de microrregiao no dataframe para strings '1'..'6'
    df_map = {}
    for _, r in df_rank.iterrows():
        mr = r.get('microrregiao', None)
        val = r.get('densidade_ego_media', None)
        if pd.isna(mr) or val is None:
            continue
        # trata valores numéricos (floats) que representem inteiros
        try:
            if isinstance(mr, (int, float)):
                mr_norm = str(int(mr))
            else:
                # remove espaços e pontos decimais estranhos
                mr_str = str(mr).strip()
                # tenta converter para float->int quando possível
                try:
                    mf = float(mr_str)
                    if mf.is_integer():
                        mr_norm = str(int(mf))
                    else:
                        mr_norm = mr_str
                except Exception:
                    mr_norm = mr_str
        except Exception:
            mr_norm = str(mr)

        try:
            df_map[mr_norm] = float(val)
        except Exception:
            # ignora valores inválidos
            continue

    microrregioes_ord = ordem
    densidades_ord = [df_map.get(m, 0.0) for m in microrregioes_ord]

    # Palette: usa colormap 'inferno' para visual intenso e agradável
    try:
        cmap = plt.get_cmap('inferno')
        colors = [matplotlib.colors.to_hex(cmap(i / max(1, len(microrregioes_ord) - 1))) for i in range(len(microrregioes_ord))]
    except Exception:
        base = ['#fde725', '#ffa600', '#f97306', '#d72728', '#9e0142', '#49006a']
        colors = [base[i % len(base)] for i in range(len(microrregioes_ord))]

    # Cria figura maior e mais elegante
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(microrregioes_ord, densidades_ord, color=colors, edgecolor='#444444', linewidth=0.8)

    # Estética: grade horizontal leve, título, e remoção do rótulo X (desnecessário)
    ax.set_title('Ranking — Densidade média da ego-subrede por Microrregião', fontsize=16, weight='bold')
    # ax.set_xlabel('Microrregião', fontsize=12)  # removido conforme solicitado
    ax.set_ylabel('Densidade média da ego-subrede', fontsize=12)
    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize=11)
    ax.grid(axis='y', color='#eeeeee')
    ax.set_axisbelow(True)

    # Ajusta limite superior para evitar que os valores fiquem cortados
    ymax = max(densidades_ord) if densidades_ord else 0
    if ymax <= 0:
        ax.set_ylim(0, 1)
    else:
        ax.set_ylim(0, ymax * 1.12)

    # Valores sobre as barras (formatados)
    ypad = ymax * 0.04 if ymax > 0 else 0.02
    for bar, val in zip(bars, densidades_ord):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + ypad, f"{val:.3f}", ha='center', va='bottom', fontsize=10, fontweight='semibold')

    # Legenda compacta à direita
    handles = [matplotlib.patches.Patch(color=colors[i], label=f"Microrregião {microrregioes_ord[i]}") for i in range(len(microrregioes_ord))]
    ax.legend(handles=handles, title='Microrregiões', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False, fontsize=10, title_fontsize=11)

    plt.tight_layout()
    plt.subplots_adjust(right=0.78, top=0.88)

    caminho_saida = os.path.join("out/parte1", "ranking_densidade_ego_microrregiao.png")
    plt.savefig(caminho_saida, bbox_inches='tight', dpi=200)
    plt.close(fig)

    print(caminho_saida)

def arvore_bfs_boaviagem_html():
    """
    Gera uma ÁRVORE BFS a partir do bairro 'Boa Viagem' em HTML interativo (pyvis).

    Cada nível da BFS é exibido como uma camada hierárquica:

        out/arvore_bfs_boaviagem.html
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
    net.show(caminho_saida, notebook=False)  # notebook=False para evitar bug de template
    print(caminho_saida)


def grafo_interativo_html():
    """
    Gera um HTML interativo com:
        - Tooltip por bairro: grau, microrregiao, densidade_ego
        - Caixa de busca por bairro
        - Botao para destacar o caminho 'Nova Descoberta -> Boa Viagem (Setubal)'

    Saida: out/grafo_interativo.html
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

    # --- 3) Carrega densidade_ego por bairro (out/ego_bairro.csv) ---
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
        "physics": { "stabilization": { "enabled": true, "iterations": 1000 } }
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

    # 10.1) Caixa de busca + botoes (logo apos <body>)
    issues_html = ""
    if issues:
        # Pequena mensagem visível no HTML para o usuário
        items = "<br>".join([f"- {i}" for i in issues])
        issues_html = f"<div style='padding:8px;border:1px solid #faa; background:#fff0f0;margin-bottom:8px;'><strong>Atenção:</strong><br>{items}</div>"

    # caixa fixa preta no canto superior-esquerdo com botões dispostos verticalmente (sempre criado)
    # Cria lista de bairros ordenada para os dropdowns
    bairros_sorted = sorted(bairros)
    bairros_options = "\n".join([f"                <option value='{b}'>{b}</option>" for b in bairros_sorted])
    
    controls_html = f"""
<style>
    /* Caixa de controles fixa e elegante */
    .gp-controls-box {{
        position: fixed;
        top: 16px;
        left: 16px;
        z-index: 9999;
        background: linear-gradient(180deg, #0b0b0b 0%, #1a1a1a 100%);
        color: #ffffff;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        min-width: 220px;
        max-width: 320px;
        font-family: Arial, Helvetica, sans-serif;
    }}
    .gp-controls-box .gp-issue {{
        background: rgba(255,80,80,0.08);
        border: 1px solid rgba(255,80,80,0.18);
        color: #ffdede;
        padding: 6px 8px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-size: 12px;
    }}
    .gp-controls-vertical {{
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}
    .gp-controls-vertical select {{
        width: 100%;
        padding: 10px 12px;
        border-radius: 8px;
        border: 2px solid rgba(255,255,255,0.2);
        background: rgba(30, 30, 30, 0.95);
        color: #ffffff;
        outline: none;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    .gp-controls-vertical select:hover {{
        border-color: rgba(255,255,255,0.4);
        background: rgba(40, 40, 40, 0.95);
    }}
    .gp-controls-vertical select:focus {{
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }}
    .gp-controls-vertical select option {{
        background: #2a2a2a;
        color: #ffffff;
        padding: 8px;
    }}
    .gp-controls-vertical button {{
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
    }}
    .gp-controls-vertical button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.6);
    }}
    /* Ajuste para telas pequenas */
    @media (max-width: 480px) {{
        .gp-controls-box {{ left: 8px; top: 8px; padding: 10px; min-width: 180px; }}
    }}
</style>

<div class="gp-controls-box">
    {f"<div class='gp-issue'>{issues_html}</div>" if issues_html else ""}
    <div class="gp-controls-vertical">
        <select id="origem-select">
            <option value="">Selecione a origem...</option>
{bairros_options}
        </select>
        <select id="destino-select">
            <option value="">Selecione o destino...</option>
{bairros_options}
        </select>
        <button onclick="calcularMenorCaminho()">Calcular Menor Caminho</button>
        <button onclick="highlightPath()">Destacar Nova Descoberta → Boa Viagem</button>
        <button onclick="resetHighlight()">Limpar Destaques</button>
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

    extra_js = """
<script type="text/javascript">
    // Nos e arestas do caminho minimo Nova Descoberta -> Boa Viagem (Setubal)
    var pathNodes = __PATH_NODES__;
    var pathEdges = __PATH_EDGES__;

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

    for (var i = 0; i < allNodes.length; i++) {
        var n = allNodes[i];
        if (n.id === nome || (n.label && n.label.toLowerCase() === nomeLower)) {
        found = n;
        break;
        }
    }

        if (!found) {
            alert("Bairro não encontrado: " + nome);
            return;
        }

    network.selectNodes([found.id]);
    network.focus(found.id, {
        scale: 1.6,
        animation: { duration: 800, easingFunction: 'easeInOutQuad' }
    });
    }
    
    function calcularMenorCaminho() {
        var origemSelect = document.getElementById('origem-select');
        var destinoSelect = document.getElementById('destino-select');
        
        if (!origemSelect || !destinoSelect) {
            alert('Select elements not found');
            return;
        }
        
        var origem = origemSelect.value;
        var destino = destinoSelect.value;
        
        if (!origem || !destino) {
            alert('Por favor, selecione a origem e o destino');
            return;
        }
        
        if (origem === destino) {
            alert('Origem e destino devem ser diferentes');
            return;
        }
        
        // Chama a função Python para calcular o menor caminho
        // Como não podemos chamar Python diretamente do JavaScript, vamos usar uma abordagem alternativa
        // Vamos destacar o caminho usando uma implementação JavaScript simples de BFS
        highlightCustomPath(origem, destino);
    }
    
    function highlightCustomPath(origem, destino) {
        // Implementação de Dijkstra para encontrar o menor caminho
        var allNodes = nodes.get();
        var allEdges = edges.get();
        var graphData = __GRAPH_DATA__;
        
        // Construir mapa de adjacência com pesos
        var adjMap = {};
        for (var i = 0; i < graphData.edges.length; i++) {
            var edge = graphData.edges[i];
            var u = edge[0];
            var v = edge[1];
            if (!adjMap[u]) adjMap[u] = [];
            if (!adjMap[v]) adjMap[v] = [];
            // Assumindo peso 1 para todas as arestas (pode ser modificado se houver pesos)
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
        
        // Criar conjunto de arestas do caminho
        var pathEdgeSet = {};
        for (var k = 0; k < path.length - 1; k++) {
            var key = [path[k], path[k+1]].sort().join("||");
            pathEdgeSet[key] = true;
        }
        
        // Limpa destaques anteriores
        resetHighlight();
        
        // Destacar arestas do caminho
        for (var i = 0; i < allEdges.length; i++) {
            var e = allEdges[i];
            var key = [e.from, e.to].sort().join("||");
            if (pathEdgeSet[key]) {
                if (e._originalColor === undefined) e._originalColor = e.color;
                e.color = { color: '#FF69B4' };  // rosa para o novo caminho
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
                // podemos deixar o restante igual (sem alterar tamanho)
            }
        }
        nodes.update(allNodes);
        
        // Centralizar no caminho
        network.fit({
            nodes: path,
            animation: { duration: 800, easingFunction: 'easeInOutQuad' }
        });
        
        console.log('Menor caminho encontrado:', path);
        console.log('Distância total:', dist[destino]);
    }

    function resetHighlight() {
    // reset das arestas
    var allEdges = edges.get();
    for (var i = 0; i < allEdges.length; i++) {
        var e = allEdges[i];
        if (e._originalColor !== undefined) {
        e.color = e._originalColor;
        }
    }
    edges.update(allEdges);

    // reset dos nos
    var allNodes = nodes.get();
    for (var i = 0; i < allNodes.length; i++) {
        var n = allNodes[i];
        if (n._originalColor !== undefined) {
        n.color = n._originalColor;
        }
    }
    nodes.update(allNodes);
    }

    function highlightPath() {
    if (!pathNodes || pathNodes.length === 0) {
        alert("Caminho Nova Descoberta → Boa Viagem (Setúbal) não encontrado nos dados.");
        return;
    }

    // Limpa quaisquer destaques anteriores
    resetHighlight();

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

    // 3) Centraliza o grafo em torno dos nos do caminho
    network.fit({
        nodes: pathNodes,
        animation: { duration: 800, easingFunction: 'easeInOutQuad' }
    });
    }
</script>
"""

    extra_js = extra_js.replace("__PATH_NODES__", path_nodes_js)
    extra_js = extra_js.replace("__PATH_EDGES__", path_edges_js)
    extra_js = extra_js.replace("__GRAPH_DATA__", graph_data_js)

    if "</body>" in html:
        html = html.replace("</body>", extra_js + "\n</body>", 1)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)

    print("Grafo interativo salvo em:", caminho_saida)






if __name__ == "__main__":
    arvore_percurso_html()
    mapa_graus_html()
    ranking_densidade_ego_microrregiao_png()
    arvore_bfs_boaviagem_html()
    grafo_interativo_html()
