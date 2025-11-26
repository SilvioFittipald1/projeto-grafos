# arquivo que define a estrutura do grafo
"""
um grafo simples que representa os bairros do recife
tem os bairros como nós e as ruas como arestas
cada aresta tem um peso que pode ser a distância
"""

class Graph:
    def __init__(self):
        """
        cria um grafo novo e vazio
        
        usa um dicionario pra guardar os bairros e seus vizinhos
        cada bairro aponta pra uma lista de tuplas (vizinho, peso)
        """
        self.adjacencia = {}

    # NÓS

    def adicionar_no(self, bairro):
        """
        coloca um bairro novo no grafo
        se ja existir, nao faz nada
        """
        if bairro not in self.adjacencia:
            self.adjacencia[bairro] = []

    def obter_nos(self):
        """
        pega a lista de todos os bairros do grafo
        """
        return list(self.adjacencia.keys())

    # ARESTAS (grafo NÃO DIRIGIDO)

    def adicionar_aresta(self, bairro1, bairro2, peso=1.0):
        """
        liga dois bairros com uma rua
        como o grafo nao e direcionado, a rua vai e volta
        """
        # cria os bairros se nao existirem
        self.adicionar_no(bairro1)
        self.adicionar_no(bairro2)

        # faz a rua de ida e volta
        self.adjacencia[bairro1].append((bairro2, peso))
        self.adjacencia[bairro2].append((bairro1, peso))

    def vizinhos(self, bairro):
        """
        mostra todos os bairros que dao pra chegar a partir de um bairro
        retorna uma lista de tuplas (bairro, distancia)
        se o bairro nao existir, retorna lista vazia
        """
        return self.adjacencia.get(bairro, [])

    # MÉTRICAS SIMPLES

    def grau(self, bairro):
        """
        conta quantas ruas chegam em um bairro
        """
        return len(self.adjacencia.get(bairro, []))

    def ordem(self):
        """
        conta quantos bairros tem no grafo
        """
        return len(self.adjacencia)

    def tamanho(self):
        """
        conta quantas ruas tem no total
        como cada rua ta contada duas vezes (ida e volta),
        divide por 2 no final
        """
        total = sum(len(vizinhos) for vizinhos in self.adjacencia.values())
        return total // 2

    def densidade(self):
        """
        calcula o quao conectado esta o grafo
        retorna um numero entre 0 e 1
        mais perto de 1 = mais conexoes entre os bairros
        """
        n = self.ordem()
        if n < 2:
            return 0.0

        e = self.tamanho()
        return (2 * e) / (n * (n - 1))
    
    def subgrafo_induzido(self, bairros):
        """
        cria um grafo menor so com os bairros que a gente quiser
        e mantem as ruas que existiam entre eles
        """
        # usa um set pra nao ter bairro repetido
        subconjunto = set(bairros)
        novo = Graph()

        # coloca so os bairros que a gente quer
        for b in subconjunto:
            if b in self.adjacencia:
                novo.adicionar_no(b)

        # ve quais ruas da pra manter
        arestas_adicionadas = set()

        for b in subconjunto:
            # pega todos os vizinhos de cada bairro
            for vizinho, peso in self.vizinhos(b):
                # se o vizinho tiver na nossa lista de bairros
                if vizinho in subconjunto:
                    # cria um jeito unico de identificar a rua
                    aresta = tuple(sorted((b, vizinho)))
                    if aresta not in arestas_adicionadas:
                        # adiciona a rua no novo grafo
                        novo.adicionar_aresta(b, vizinho, peso)
                        arestas_adicionadas.add(aresta)

        return novo

    
