# src/graphs/graph.py
"""
Implementação simples de um grafo NÃO DIRIGIDO usando lista de adjacência.

- Cada nó será um bairro do Recife (string, ex.: "Boa Viagem").
- As arestas têm um peso (float), que pode representar distância, custo etc.
"""

class Graph:
    def __init__(self):
        """
        Cria um grafo vazio.

        Atributo principal:
        - adjacencia: dicionário onde
            chave   = nome do bairro (nó)
            valor   = lista de vizinhos, no formato [(bairro_vizinho, peso), ...]
        """
        self.adjacencia = {}

    # -------------------------------------------------
    # NÓS
    # -------------------------------------------------

    def adicionar_no(self, bairro):
        """
        Adiciona um novo nó (bairro) no grafo.

        Se o bairro já existir, não faz nada.
        """
        if bairro not in self.adjacencia:
            self.adjacencia[bairro] = []

    def obter_nos(self):
        """
        Retorna uma lista com todos os bairros (nós) do grafo.
        """
        return list(self.adjacencia.keys())

    # -------------------------------------------------
    # ARESTAS (grafo NÃO DIRIGIDO)
    # -------------------------------------------------

    def adicionar_aresta(self, bairro1, bairro2, peso=1.0):
        """
        Adiciona uma aresta entre dois bairros.

        Como o grafo é NÃO DIRIGIDO:
        - adiciona bairro2 na lista de vizinhos de bairro1
        - e também bairro1 na lista de vizinhos de bairro2
        """
        # Garante que os bairros existem como nós
        self.adicionar_no(bairro1)
        self.adicionar_no(bairro2)

        # Adiciona ligação bairro1 -> bairro2
        self.adjacencia[bairro1].append((bairro2, peso))
        # Adiciona ligação bairro2 -> bairro1
        self.adjacencia[bairro2].append((bairro1, peso))

    def vizinhos(self, bairro):
        """
        Retorna a lista de vizinhos de um bairro.

        Formato da lista:
            [(bairro_vizinho, peso), ...]
        Se o bairro não existir no grafo, retorna lista vazia.
        """
        return self.adjacencia.get(bairro, [])

    # -------------------------------------------------
    # MÉTRICAS SIMPLES
    # -------------------------------------------------

    def grau(self, bairro):
        """
        Retorna o grau de um bairro (quantas arestas incidem nele).
        """
        return len(self.adjacencia.get(bairro, []))

    def ordem(self):
        """
        Retorna a ORDEM do grafo: número de nós (bairros).
        """
        return len(self.adjacencia)

    def tamanho(self):
        """
        Retorna o TAMANHO do grafo: número de arestas.

        Como o grafo é NÃO DIRIGIDO, cada aresta aparece duas vezes
        na lista de adjacência (uma em cada extremidade).
        Por isso, somamos tudo e dividimos por 2.
        """
        total = sum(len(vizinhos) for vizinhos in self.adjacencia.values())
        return total // 2

    def densidade(self):
        """
        Calcula a densidade do grafo:

            densidade = 2 * |E| / (|V| * (|V| - 1))

        onde:
            |V| = número de nós  (ordem)
            |E| = número de arestas (tamanho)
        """
        n = self.ordem()
        if n < 2:
            return 0.0

        e = self.tamanho()
        return (2 * e) / (n * (n - 1))
    
    def subgrafo_induzido(self, bairros):
        """
        Cria um novo grafo contendo apenas os bairros da lista
        e as arestas entre eles (do grafo original).

        - bairros: lista ou conjunto de nomes de bairros.
        - O grafo resultante também é NÃO DIRIGIDO.
        """
        subconjunto = set(bairros)
        novo = Graph()

        # Adiciona os nós do subconjunto
        for b in subconjunto:
            if b in self.adjacencia:
                novo.adicionar_no(b)

        # Adiciona as arestas entre nós do subconjunto,
        # cuidando para não duplicar (grafo não dirigido).
        arestas_adicionadas = set()

        for b in subconjunto:
            for vizinho, peso in self.vizinhos(b):
                if vizinho in subconjunto:
                    # Representação canônica da aresta não dirigida
                    aresta = tuple(sorted((b, vizinho)))
                    if aresta not in arestas_adicionadas:
                        novo.adicionar_aresta(b, vizinho, peso)
                        arestas_adicionadas.add(aresta)

        return novo

    
