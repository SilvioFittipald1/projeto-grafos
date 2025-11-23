# src/viz.py

import os
import json
import pandas as pd
from pyvis.network import Network
from .graphs.io import carregar_grafo_recife
from .graphs.algorithms import bfs_arvore
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

OUT_DIR = "out"


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


def arvore_percurso_png(
    caminho_json: str | None = None,
    caminho_saida: str | None = None
):
    """
    PASSO 7:

    - Lê o percurso Nova Descoberta -> Boa Viagem (Setúbal) do JSON.
    - Constrói a "árvore de caminho" (subgrafo apenas com os nós e arestas do percurso).
    - Gera uma visualização simples em linha e salva em out/arvore_percurso.png.

    A visualização é uma linha de nós igualmente espaçados, conectados na ordem do caminho.
    """

    # 1) Carrega origem, destino e caminho a partir do JSON do PASSO 6
    origem, destino_rotulo, caminho = percurso_nova_descoberta_setubal(
        caminho_json
    )

    # Define o arquivo de saída
    if caminho_saida is None:
        caminho_saida = os.path.join(OUT_DIR, "arvore_percurso.png")

    os.makedirs(OUT_DIR, exist_ok=True)

    # 2) Prepara os rótulos dos nós para exibição
    #    - usamos os nomes do caminho
    #    - mas substituímos o último pela string de destino (ex.: "Boa Viagem (Setúbal)")
    labels = list(caminho)
    if destino_rotulo and len(labels) > 0:
        labels[-1] = destino_rotulo

    n = len(labels)
    x_coords = list(range(n))
    y_coords = [0] * n  # todos na mesma linha horizontal

    # 3) Cria a figura
    plt.figure(figsize=(max(6, n * 1.5), 4))

    # Desenha as arestas (linhas entre nós consecutivos)
    for i in range(n - 1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i + 1], y_coords[i + 1]
        plt.plot([x1, x2], [y1, y2], linewidth=2)

    # Desenha os nós como pontos
    plt.scatter(x_coords, y_coords, s=200)

    # 4) Adiciona os rótulos dos nós
    for x, y, label in zip(x_coords, y_coords, labels):
        plt.text(
            x,
            y + 0.05,   # desloca um pouco pra cima do ponto
            label,
            ha="center",
            va="bottom",
            rotation=15  # leve inclinação pra caber melhor
        )

    # Remove eixos para ficar mais "clean"
    plt.axis("off")
    plt.tight_layout()

    # 5) Salva a figura
    plt.savefig(caminho_saida, bbox_inches="tight")
    plt.close()

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
        caminho_saida = os.path.join(OUT_DIR, "arvore_percurso.html")

    os.makedirs(OUT_DIR, exist_ok=True)

    # 2) Monta os rótulos dos nós
    labels = list(caminho)
    if destino_rotulo and len(labels) > 0:
        labels[-1] = destino_rotulo  # exibe "Boa Viagem (Setúbal)" no último nó

    # 3) Cria a rede pyvis
    net = Network(height="600px", width="100%", directed=False)
    net.barnes_hut()  # layout físico bonitinho

    # Adiciona nós
    for i, label in enumerate(labels):
        titulo = label
        # Destacar origem e destino (opcional)
        if i == 0:
            # origem
            net.add_node(label, label=label, title=titulo, color="#8ecae6")
        elif i == len(labels) - 1:
            # destino
            net.add_node(label, label=label, title=titulo, color="#ffb703")
        else:
            net.add_node(label, label=label, title=titulo)

    # Adiciona arestas entre nós consecutivos
    for i in range(len(labels) - 1):
        u = labels[i]
        v = labels[i + 1]
        net.add_edge(u, v)

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



DATA_DIR = "data"
OUT_DIR = "out"


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

    # 3) Cria a rede pyvis
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000"
    )
    net.barnes_hut()

    # 4) Adiciona nós com cor baseada no grau
    for bairro in bairros:
        grau = graus[bairro]
        cor = cor_por_grau(grau, gmin, gmax)
        title = f"{bairro}<br>Grau: {grau}"

        net.add_node(
            bairro,
            label=bairro,
            title=title,
            color=cor
        )

    # 5) Adiciona arestas (sem duplicar, grafo não dirigido)
    arestas_adicionadas = set()
    for b in bairros:
        for vizinho, peso in grafo.vizinhos(b):
            if vizinho not in graus:
                # caso raro: bairro exista no grafo mas não em graus.csv
                continue
            aresta = tuple(sorted((b, vizinho)))
            if aresta in arestas_adicionadas:
                continue
            net.add_edge(b, vizinho, value=peso)
            arestas_adicionadas.add(aresta)

    # 6) Salva o HTML
    caminho_saida = os.path.join(OUT_DIR, "mapa_graus.html")
    net.show(caminho_saida, notebook=False)  # notebook=False para evitar o bug do template
    print(caminho_saida)

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

    # 6) Cria o gráfico de barras
    plt.figure(figsize=(8, 5))
    plt.bar(microrregioes, densidades_medias)
    plt.xlabel("Microrregião")
    plt.ylabel("Densidade média da ego-subrede")
    plt.title("Ranking de densidade de ego-subrede por microrregião")
    plt.tight_layout()

    caminho_saida = os.path.join(OUT_DIR, "ranking_densidade_ego_microrregiao.png")
    plt.savefig(caminho_saida, bbox_inches="tight")
    plt.close()

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


    caminho_saida = os.path.join(OUT_DIR, "arvore_bfs_boaviagem.html")
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

    # --- 2) Carrega grau por bairro (out/graus.csv) ---
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

        # Tentamos ler chave "caminho" (como foi definido no passo 6)
        caminho = dados.get("caminho") or dados.get("caminho_bairros") or []
        if isinstance(caminho, list) and len(caminho) >= 2:
            path_nodes = caminho
            # Cria arestas entre consecutivos do caminho
            for i in range(len(caminho) - 1):
                u = caminho[i]
                v = caminho[i + 1]
                path_edges.append([u, v])
    else:
        print("Aviso: JSON do percurso Nova Descoberta -> Setubal nao encontrado. "
              "Botoes de destaque do caminho ainda serao gerados, mas nao terao efeito.")

    # --- 5) Descobre min/max grau para gradiente de cores ---
    gmin = min(graus.values())
    gmax = max(graus.values())

    # --- 6) Cria a rede pyvis ---
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000"
    )
    net.barnes_hut()

    # --- 7) Adiciona nos com tooltip (grau, microrregiao, densidade_ego) ---
    for bairro in bairros:
        grau = graus.get(bairro, grafo.grau(bairro))
        microrregiao = bairro_para_micro.get(bairro, "NA")
        dens = dens_ego.get(bairro, None)
        if dens is None or pd.isna(dens):
            dens_str = "-"
        else:
            dens_str = f"{dens:.4f}"

        # Tooltip HTML
        title = (
            f"Bairro: {bairro}<br>"
            f"Grau: {grau}<br>"
            f"Microrregiao: {microrregiao}<br>"
            f"Densidade ego: {dens_str}"
        )

        # Cor base pela funcao cor_por_grau (reaproveitada do mapa de graus)
        try:
            cor = cor_por_grau(grau, gmin, gmax)
        except NameError:
            # Se por acaso cor_por_grau nao existir, usa cor padrao
            cor = "#97c2fc"

        net.add_node(
            bairro,
            label=bairro,
            title=title,
            color=cor
        )

    # --- 8) Adiciona arestas do grafo (sem duplicar) ---
    arestas_adicionadas = set()
    for b in bairros:
        for vizinho, peso in grafo.vizinhos(b):
            aresta = tuple(sorted((b, vizinho)))
            if aresta in arestas_adicionadas:
                continue
            net.add_edge(b, vizinho, value=float(peso))
            arestas_adicionadas.add(aresta)

    # --- 9) Gera o HTML base com pyvis ---
    caminho_saida = os.path.join(OUT_DIR, "grafo_interativo.html")
    net.show(caminho_saida, notebook=False)
    print(caminho_saida)

        # --- 10) Pos-processa o HTML para adicionar busca + botoes + JS de destaque ---
    with open(caminho_saida, "r", encoding="utf-8") as f:
        html = f.read()

    # 10.1) Caixa de busca + botoes (logo apos <body>)
    controls_html = """
<h3>Grafo interativo de bairros do Recife</h3>
<div style="margin-bottom:10px;">
  <input id="busca-bairro" type="text"
         placeholder="Digite o nome do bairro..."
         style="width:260px; padding:4px;" />
  <button onclick="buscarBairro()">Buscar bairro</button>
  <button onclick="highlightPath()">Destacar caminho Nova Descoberta &rarr; Boa Viagem (Setubal)</button>
  <button onclick="resetHighlight()">Limpar destaque</button>
</div>
"""
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + controls_html, 1)

    # 10.2) Script JS extra com busca + destaque do caminho
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
      alert("Bairro nao encontrado: " + nome);
      return;
    }

    network.selectNodes([found.id]);
    network.focus(found.id, {
      scale: 1.6,
      animation: { duration: 800, easingFunction: 'easeInOutQuad' }
    });
  }

  function resetHighlight() {
    // reset das arestas
    var allEdges = edges.get();
    for (var i = 0; i < allEdges.length; i++) {
      var e = allEdges[i];
      if (e.originalColor) {
        e.color = e.originalColor;
      } else {
        e.color = undefined;
      }
      e.width = 1;
    }
    edges.update(allEdges);

    // reset dos nos
    var allNodes = nodes.get();
    for (var i = 0; i < allNodes.length; i++) {
      var n = allNodes[i];
      if (n.originalColor) {
        n.color = n.originalColor;
      }
    }
    nodes.update(allNodes);
  }

  function highlightPath() {
    if (!pathNodes || pathNodes.length === 0) {
      alert("Caminho Nova Descoberta -> Boa Viagem (Setubal) nao encontrado nos dados.");
      return;
    }

    // Limpa quaisquer destaques anteriores
    resetHighlight();

    // 1) DESTACAR APENAS AS ARESTAS QUE ESTAO EM pathEdgeSet
    var allEdges = edges.get();
    for (var i = 0; i < allEdges.length; i++) {
      var e = allEdges[i];

      // chave canonica da aresta atual
      var key = [e.from, e.to].sort().join("||");

      if (pathEdgeSet[key]) {
        // Guarda a cor original se ainda nao guardou
        if (!e.originalColor) {
          e.originalColor = e.color;
        }
        // Destaca a aresta do caminho
        e.color = { color: '#ff0000' };  // vermelho
        e.width = 4;                     // mais grossa
      }
    }
    edges.update(allEdges);

    // 2) DESTACAR OS NOS QUE ESTAO EM pathNodes
    var allNodes = nodes.get();
    for (var i = 0; i < allNodes.length; i++) {
      var n = allNodes[i];
      if (pathNodes.indexOf(n.id) !== -1) {
        // Guarda cor original se ainda nao guardou
        if (!n.originalColor) {
          n.originalColor = n.color;
        }
        // Destaca o no (borda vermelha, fundo mais claro)
        n.color = { background: '#ffcccc', border: '#ff0000' };
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

    if "</body>" in html:
        html = html.replace("</body>", extra_js + "\n</body>", 1)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)

    print("Grafo interativo salvo em:", caminho_saida)






if __name__ == "__main__":
    arvore_percurso_png()
    arvore_percurso_html()
    mapa_graus_html()
    ranking_densidade_ego_microrregiao_png()
    arvore_bfs_boaviagem_html()
    grafo_interativo_html()
