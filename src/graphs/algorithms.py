import networkx as nx


def bfs(graph, start):
    """Breadth-first search: retorna lista de nós na ordem de visitação.

    `graph` deve expor método `neighbors(node)`.
    """
    from collections import deque

    start = start
    visited = set()
    order = []
    q = deque()
    q.append(start)
    visited.add(start)

    while q:
        v = q.popleft()
        order.append(v)
        for w in graph.neighbors(v):
            if w not in visited:
                visited.add(w)
                q.append(w)

    return order

def dfs(graph, start):
    """Depth-first search (iterativo). Retorna lista de nós na ordem de visitação."""
    visited = set()
    order = []
    stack = [start]

    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        order.append(v)
        # empilha vizinhos em ordem (não garantida); invert para comportamento mais natural
        nbrs = list(graph.neighbors(v))
        for w in reversed(nbrs):
            if w not in visited:
                stack.append(w)

    return order

def dijkstra(graph, start):
    """Dijkstra: retorna (dist, prev) onde dist[node]=custo mínimo de start e
    prev[node]=predecessor no caminho mínimo (ou None). Usa 'peso' nas arestas.

    `graph` deve expor atributo `adj` ou método `neighbors` e fornecer peso.
    """
    import heapq

    dist = {}
    prev = {}
    # inicializa dist com infinito para todos os nós conhecidos
    for n in graph.nodes():
        dist[n] = float('inf')
        prev[n] = None

    if start not in dist:
        return dist, prev

    dist[start] = 0.0
    heap = [(0.0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, edata in graph.adj.get(u, {}).items():
            w = edata.get('peso', 1.0)
            alt = dist[u] + float(w)
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))

    return dist, prev

def bellman_ford(graph, start):
    """Bellman-Ford: retorna (dist, prev, has_negative_cycle)

    Útil para arestas com pesos possivelmente negativos (não usado na Parte 1).
    """
    dist = {}
    prev = {}
    for n in graph.nodes():
        dist[n] = float('inf')
        prev[n] = None

    if start not in dist:
        return dist, prev, False

    dist[start] = 0.0
    nodes = graph.nodes()
    # relaxa |V|-1 vezes
    for _ in range(len(nodes) - 1):
        changed = False
        for u, v, edata in graph.edges():
            w = edata.get('peso', 1.0)
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                changed = True
            if dist[v] + w < dist[u]:
                dist[u] = dist[v] + w
                prev[u] = v
                changed = True
        if not changed:
            break

    # checa ciclo negativo
    has_neg = False
    for u, v, edata in graph.edges():
        w = edata.get('peso', 1.0)
        if dist[u] + w < dist[v]:
            has_neg = True
            break

    return dist, prev, has_neg


def bfs_using_networkx(graph, start):
    """Usa networkx.bfs_tree convertendo o grafo se necessário."""
    Gnx = graph.to_networkx() if hasattr(graph, 'to_networkx') else None
    if Gnx is None:
        Gnx = nx.Graph()
        for n in graph.nodes():
            Gnx.add_node(n)
        for u, v, _ in graph.edges():
            Gnx.add_edge(u, v)
    tree = nx.bfs_tree(Gnx, start)
    return list(tree.nodes())


def dijkstra_using_networkx(graph, start):
    """Usa nx.single_source_dijkstra quando possível."""
    Gnx = graph.to_networkx() if hasattr(graph, 'to_networkx') else None
    if Gnx is None:
        Gnx = nx.Graph()
        for n in graph.nodes():
            Gnx.add_node(n)
        for u, v, data in graph.edges():
            Gnx.add_edge(u, v, **(data or {}))
    dist_map, paths = nx.single_source_dijkstra(Gnx, start, weight='peso')
    prev = {n: None for n in Gnx.nodes()}
    for dest, path in paths.items():
        if len(path) >= 2:
            prev[dest] = path[-2]
    dist = {n: float('inf') for n in Gnx.nodes()}
    for k, v in dist_map.items():
        dist[k] = v
    return dist, prev


def bellman_ford_using_networkx(graph, start):
    """Usa nx.single_source_bellman_ford quando possível."""
    Gnx = graph.to_networkx() if hasattr(graph, 'to_networkx') else None
    if Gnx is None:
        Gnx = nx.DiGraph()
        for n in graph.nodes():
            Gnx.add_node(n)
        for u, v, data in graph.edges():
            Gnx.add_edge(u, v, **(data or {}))
    length, path = nx.single_source_bellman_ford(Gnx, start, weight='peso')
    prev = {n: None for n in Gnx.nodes()}
    for dest, p in path.items():
        if len(p) >= 2:
            prev[dest] = p[-2]
    dist = {n: float('inf') for n in Gnx.nodes()}
    for k, v in length.items():
        dist[k] = v
    return dist, prev, False


# Se networkx estiver disponível, expõe funções que usam suas rotinas otimizadas.
try:
    import networkx as nx  # type: ignore
    NX_AVAILABLE = True
except Exception:
    nx = None
    NX_AVAILABLE = False


def bfs_using_networkx(graph, start):
    if not NX_AVAILABLE:
        return bfs(graph, start)
    # obtém uma representação networkx do grafo
    Gnx = None
    if hasattr(graph, 'to_networkx'):
        Gnx = graph.to_networkx()
    if Gnx is None:
        Gnx = nx.Graph()
        for n in graph.nodes():
            Gnx.add_node(n)
        for u, v, _ in graph.edges():
            Gnx.add_edge(u, v)
    # usa bfs_tree para garantir ordem de níveis
    try:
        tree = nx.bfs_tree(Gnx, start)
        return list(tree.nodes())
    except Exception:
        return bfs(graph, start)


def dijkstra_using_networkx(graph, start):
    if not NX_AVAILABLE:
        return dijkstra(graph, start)
    Gnx = None
    if hasattr(graph, 'to_networkx'):
        Gnx = graph.to_networkx()
    if Gnx is None:
        Gnx = nx.Graph()
        for n in graph.nodes():
            Gnx.add_node(n)
        for u, v, data in graph.edges():
            Gnx.add_edge(u, v, **(data or {}))
    try:
        dist_map, paths = nx.single_source_dijkstra(Gnx, start, weight='peso')
    except Exception:
        return dijkstra(graph, start)
    # constrói prev a partir de paths
    prev = {n: None for n in Gnx.nodes()}
    for dest, path in paths.items():
        if len(path) >= 2:
            prev[dest] = path[-2]
    dist = {n: float('inf') for n in Gnx.nodes()}
    for k, v in dist_map.items():
        dist[k] = v
    return dist, prev


def bellman_ford_using_networkx(graph, start):
    if not NX_AVAILABLE:
        return bellman_ford(graph, start)
    Gnx = None
    if hasattr(graph, 'to_networkx'):
        Gnx = graph.to_networkx()
    if Gnx is None:
        Gnx = nx.DiGraph()
        for n in graph.nodes():
            Gnx.add_node(n)
        for u, v, data in graph.edges():
            # para Bellman-Ford usaremos direção arbitrária (u->v)
            Gnx.add_edge(u, v, **(data or {}))
    try:
        length, path = nx.single_source_bellman_ford(Gnx, start, weight='peso')
        # length is a dict of distances, path is dict of paths
        prev = {n: None for n in Gnx.nodes()}
        for dest, p in path.items():
            if len(p) >= 2:
                prev[dest] = p[-2]
        dist = {n: float('inf') for n in Gnx.nodes()}
        for k, v in length.items():
            dist[k] = v
        # networkx raises if negative cycle reachable; here assume no
        return dist, prev, False
    except Exception:
        return bellman_ford(graph, start)