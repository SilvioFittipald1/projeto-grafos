class Graph:
    def __init__(self):
        """Cria um grafo vazio."""
        self.adjacencia = {}

    def adicionar_no(self, bairro):
        """Adiciona um nó ao grafo."""
        if bairro not in self.adjacencia:
            self.adjacencia[bairro] = []

    def obter_nos(self):
        """Retorna a lista de todos os nós do grafo."""
        return list(self.adjacencia.keys())

    def adicionar_aresta(self, bairro1, bairro2, peso=1.0):
        """Adiciona uma aresta não-direcionada entre dois nós."""
        self.adicionar_no(bairro1)
        self.adicionar_no(bairro2)
        self.adjacencia[bairro1].append((bairro2, peso))
        self.adjacencia[bairro2].append((bairro1, peso))

    def vizinhos(self, bairro):
        """Retorna os vizinhos de um nó como lista de tuplas (vizinho, peso)."""
        return self.adjacencia.get(bairro, [])

    def grau(self, bairro):
        """Retorna o grau de um nó."""
        return len(self.adjacencia.get(bairro, []))

    def ordem(self):
        """Retorna o número de nós do grafo."""
        return len(self.adjacencia)

    def tamanho(self):
        """Retorna o número de arestas do grafo."""
        total = sum(len(vizinhos) for vizinhos in self.adjacencia.values())
        return total // 2

    def densidade(self):
        """Calcula a densidade do grafo."""
        n = self.ordem()
        if n < 2:
            return 0.0

        e = self.tamanho()
        return (2 * e) / (n * (n - 1))
    
    def subgrafo_induzido(self, bairros):
        """Cria um subgrafo induzido por um conjunto de nós."""
        subconjunto = set(bairros)
        novo = Graph()

        for b in subconjunto:
            if b in self.adjacencia:
                novo.adicionar_no(b)

        arestas_adicionadas = set()

        for b in subconjunto:
            for vizinho, peso in self.vizinhos(b):
                if vizinho in subconjunto:
                    aresta = tuple(sorted((b, vizinho)))
                    if aresta not in arestas_adicionadas:
                        novo.adicionar_aresta(b, vizinho, peso)
                        arestas_adicionadas.add(aresta)

        return novo

    
