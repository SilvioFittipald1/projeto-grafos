import networkx as nx


class Graph:
    """Grafo não-direcionado simples com atributos de aresta.

    A estrutura interna é um dicionário de adjacência:
        { node: { neighbor: { 'peso': float, 'logradouro': str, 'observacao': str } } }
    """
    def __init__(self):
        self.adj = {}
        # atributos por nó (microrregiao, etc.)
        self.node_attrs = {}

    def _normalize_node(self, name):
        """Normalização mínima de nomes: trata alias de Setúbal para Boa Viagem."""
        if name is None:
            return None
        n = name.strip()
        # Se for a forma 'Boa Viagem (Setúbal)' considerar nó 'Boa Viagem'
        if n.lower().startswith("boa viagem") and "set" in n.lower():
            return "Boa Viagem"
        if n.lower() in ("setúbal", "setubal"):
            return "Boa Viagem"
        return n

    def add_node(self, node, **attrs):
        node = self._normalize_node(node)
        if node not in self.adj:
            self.adj[node] = {}
        if attrs:
            self.node_attrs.setdefault(node, {}).update(attrs)

    def add_edge(self, u, v, peso=1.0, logradouro="", observacao=""):
        u = self._normalize_node(u)
        v = self._normalize_node(v)
        if u is None or v is None:
            return
        if u == v:
            # ignora auto-loops
            return

        # garante nós
        if u not in self.adj:
            self.adj[u] = {}
        if v not in self.adj:
            self.adj[v] = {}

        edge_data = {"peso": float(peso), "logradouro": logradouro, "observacao": observacao}

        # adiciona em ambos sentidos (grafo não-direcionado)
        self.adj[u][v] = edge_data
        self.adj[v][u] = edge_data

    def neighbors(self, node):
        node = self._normalize_node(node)
        return list(self.adj.get(node, {}).keys())

    def degree(self, node):
        node = self._normalize_node(node)
        return len(self.adj.get(node, {}))

    def nodes(self):
        return list(self.adj.keys())

    def edges(self):
        seen = set()
        for u, nbrs in self.adj.items():
            for v, data in nbrs.items():
                key = tuple(sorted((u, v)))
                if key in seen:
                    continue
                seen.add(key)
                yield (u, v, data)

    def number_of_nodes(self):
        return len(self.adj)

    def number_of_edges(self):
        # cada aresta armazenada duas vezes
        return sum(len(nbrs) for nbrs in self.adj.values()) // 2

    def to_networkx(self):
        """Converte para um objeto networkx.Graph quando disponível.

        Retorna None se networkx não estiver instalado.
        """
        G = nx.Graph()
        # adiciona nós com atributos
        for n in set(list(self.adj.keys()) + list(self.node_attrs.keys())):
            attrs = self.node_attrs.get(n, {})
            G.add_node(n, **attrs)

        for u, v, data in self.edges():
            # data já é um dicionário com 'peso', 'logradouro', 'observacao'
            G.add_edge(u, v, **(data or {}))

        return G