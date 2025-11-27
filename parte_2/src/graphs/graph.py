class Graph:
    """Grafo não-direcionado para representar lutadores do UFC e suas conexões."""
    
    def __init__(self):
        """Cria um grafo vazio."""
        self.adjacencia = {}
        self.vitorias = {}

    def adicionar_no(self, lutador):
        """Adiciona um nó (lutador) ao grafo."""
        if lutador not in self.adjacencia:
            self.adjacencia[lutador] = []
            self.vitorias[lutador] = 0

    def obter_nos(self):
        """Retorna a lista de todos os nós (lutadores) do grafo."""
        return list(self.adjacencia.keys())

    def adicionar_aresta(self, lutador1, lutador2, peso=1.0):
        """Adiciona uma aresta não-direcionada entre dois lutadores."""
        self.adicionar_no(lutador1)
        self.adicionar_no(lutador2)
        self.adjacencia[lutador1].append((lutador2, peso))
        self.adjacencia[lutador2].append((lutador1, peso))

    def grau(self, lutador):
        """Retorna o grau de um lutador (número de lutas/conexões)."""
        return len(self.adjacencia.get(lutador, []))

    def ordem(self):
        """Retorna o número de nós (lutadores) do grafo."""
        return len(self.adjacencia)

    def tamanho(self):
        """Retorna o número de arestas (lutas) do grafo."""
        total = sum(len(vizinhos) for vizinhos in self.adjacencia.values())
        return total // 2

    def densidade(self):
        """Calcula a densidade do grafo."""
        n = self.ordem()
        if n < 2:
            return 0.0

        e = self.tamanho()
        return (2 * e) / (n * (n - 1))
    
    def vizinhos(self, lutador):
        """Retorna a lista de vizinhos (oponentes) de um lutador com seus pesos."""
        return self.adjacencia.get(lutador, [])
    
    def registrar_vitoria(self, lutador):
        """Registra uma vitória para um lutador."""
        if lutador in self.vitorias:
            self.vitorias[lutador] += 1
        else:
            self.adicionar_no(lutador)
            self.vitorias[lutador] = 1
    
    def obter_vitorias(self, lutador):
        """Retorna o número de vitórias de um lutador."""
        return self.vitorias.get(lutador, 0)
    
    def obter_todas_vitorias(self):
        """Retorna um dicionário com o número de vitórias de todos os lutadores."""
        return self.vitorias.copy()
    
    def subgrafo_induzido(self, lutadores):
        """Cria um subgrafo induzido por um conjunto de lutadores."""
        subconjunto = set(lutadores)
        novo = Graph()

        for lutador in subconjunto:
            if lutador in self.adjacencia:
                novo.adicionar_no(lutador)

        arestas_adicionadas = set()

        for lutador in subconjunto:
            for vizinho, peso in self.vizinhos(lutador):
                if vizinho in subconjunto:
                    aresta = tuple(sorted((lutador, vizinho)))
                    if aresta not in arestas_adicionadas:
                        novo.adicionar_aresta(lutador, vizinho, peso)
                        arestas_adicionadas.add(aresta)

        return novo

