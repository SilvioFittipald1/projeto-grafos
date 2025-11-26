import heapq
from math import inf
from .graph import Graph
from collections import deque


def dijkstra(grafo: Graph, origem: str, destino: str):
    """
    Algoritmo de Dijkstra para encontrar o caminho mínimo entre dois bairros.
    """
    # Se origem ou destino não estiverem no grafo, já falha
    if origem not in grafo.adjacencia or destino not in grafo.adjacencia:
        return inf, []

    # Distâncias iniciais: infinito pra todo mundo, 0 pra origem
    dist = {no: inf for no in grafo.obter_nos()}
    dist[origem] = 0.0

    # Predecessor para reconstruir o caminho depois
    anterior = {}

    # Fila de prioridade (min-heap) com (distância, nó)
    fila = [(0.0, origem)]

    while fila:
        dist_atual, u = heapq.heappop(fila)

        # Se pegarmos uma entrada desatualizada, pula
        if dist_atual > dist[u]:
            continue

        # Se chegarmos no destino, podemos parar
        if u == destino:
            break

        # Relaxa as arestas a partir de u
        for v, peso in grafo.vizinhos(u):
            novo_custo = dist[u] + float(peso)
            if novo_custo < dist[v]:
                dist[v] = novo_custo
                anterior[v] = u
                heapq.heappush(fila, (novo_custo, v))

    # Se destino não foi alcançado
    if dist[destino] == inf:
        return inf, []

    # Reconstrói o caminho de trás pra frente: destino > ... > origem
    caminho = []
    atual = destino
    while atual != origem:
        caminho.append(atual)
        atual = anterior[atual]
    caminho.append(origem)
    caminho.reverse()  # agora origem > ... > destino

    return dist[destino], caminho


def bfs_arvore(grafo: Graph, origem: str):
    """
    Busca em Largura (BFS) a partir de 'origem', construindo a ÁRVORE BFS.
    """
    if origem not in grafo.adjacencia:
        raise ValueError(f"Bairro de origem '{origem}' não existe no grafo.")

    visitado = set()
    pai = {}
    nivel = {}

    fila = deque()

    visitado.add(origem)
    pai[origem] = None
    nivel[origem] = 0
    fila.append(origem)

    while fila:
        atual = fila.popleft()
        for vizinho, _peso in grafo.vizinhos(atual):
            if vizinho not in visitado:
                visitado.add(vizinho)
                pai[vizinho] = atual
                nivel[vizinho] = nivel[atual] + 1
                fila.append(vizinho)

    return pai, nivel


def bfs_caminho(grafo: Graph, origem: str, destino: str):
    """
    BFS para encontrar o menor caminho (em número de arestas) entre origem e destino.
    """
    if origem not in grafo.adjacencia or destino not in grafo.adjacencia:
        return []
    
    if origem == destino:
        return [origem]
    
    visitado = set()
    anterior = {}
    fila = deque([origem])
    visitado.add(origem)
    anterior[origem] = None
    
    encontrou = False
    
    while fila and not encontrou:
        atual = fila.popleft()
        
        for vizinho, _ in grafo.vizinhos(atual):
            if vizinho not in visitado:
                visitado.add(vizinho)
                anterior[vizinho] = atual
                fila.append(vizinho)
                
                if vizinho == destino:
                    encontrou = True
                    break
    
    if not encontrou:
        return []
    
    # Reconstrói o caminho
    caminho = []
    no_atual = destino
    while no_atual is not None:
        caminho.append(no_atual)
        no_atual = anterior[no_atual]
    
    caminho.reverse()
    return caminho


def dfs_arvore(grafo: Graph, origem: str):
    """
    Busca em Profundidade (DFS) a partir de 'origem', construindo a ÁRVORE DFS.
    """
    if origem not in grafo.adjacencia:
        raise ValueError(f"Bairro de origem '{origem}' não existe no grafo.")
    
    visitado = set()
    pai = {}
    descoberta = {}
    pilha = [origem]
    contador = 0
    
    visitado.add(origem)
    pai[origem] = None
    descoberta[origem] = contador
    contador += 1
    
    while pilha:
        atual = pilha.pop()
        
        # Visita vizinhos em ordem reversa
        vizinhos = list(grafo.vizinhos(atual))
        for vizinho, _ in reversed(vizinhos):
            if vizinho not in visitado:
                visitado.add(vizinho)
                pai[vizinho] = atual
                descoberta[vizinho] = contador
                contador += 1
                pilha.append(vizinho)
    
    return pai, descoberta


def dfs_caminho(grafo: Graph, origem: str, destino: str):
    """
    DFS para encontrar UM caminho qualquer entre origem e destino.
    Não garante ser o menor caminho.
    """
    if origem not in grafo.adjacencia or destino not in grafo.adjacencia:
        return []
    
    if origem == destino:
        return [origem]
    
    visitado = set()
    caminho_atual = []
    resultado = []
    
    def dfs_recursivo(no_atual):
        nonlocal resultado
        if resultado:  
            return
            
        visitado.add(no_atual)
        caminho_atual.append(no_atual)
        
        if no_atual == destino:
            resultado = caminho_atual.copy()
            return
        
        for vizinho, _ in grafo.vizinhos(no_atual):
            if vizinho not in visitado:
                dfs_recursivo(vizinho)
                if resultado:  
                    return

        caminho_atual.pop()
    
    dfs_recursivo(origem)
    return resultado


def bellman_ford(grafo: Graph, origem: str):
    """
    Algoritmo de Bellman-Ford para encontrar caminhos mínimos a partir da origem.
    Detecta ciclos negativos.
    """
    if origem not in grafo.adjacencia:
        raise ValueError(f"Bairro de origem '{origem}' não existe no grafo.")
    
    nos = list(grafo.obter_nos())
    dist = {no: inf for no in nos}
    anterior = {no: None for no in nos}
    dist[origem] = 0.0
    
    # Relaxamento das arestas |V| - 1 vezes
    for _ in range(len(nos) - 1):
        houve_mudanca = False
        
        for u in nos:
            if dist[u] == inf:
                continue
                
            for v, peso in grafo.vizinhos(u):
                peso_float = float(peso)
                if dist[u] + peso_float < dist[v]:
                    dist[v] = dist[u] + peso_float
                    anterior[v] = u
                    houve_mudanca = True
        
        # Otimização: se não houve mudança, pode parar antes
        if not houve_mudanca:
            break
    
    # Verificação de ciclos negativos
    tem_ciclo_negativo = False
    for u in nos:
        if dist[u] == inf:
            continue
            
        for v, peso in grafo.vizinhos(u):
            peso_float = float(peso)
            if dist[u] + peso_float < dist[v]:
                tem_ciclo_negativo = True
                break
        if tem_ciclo_negativo:
            break
    
    return dist, anterior, tem_ciclo_negativo


def bellman_ford_caminho(grafo: Graph, origem: str, destino: str):
    """
    Bellman-Ford para encontrar caminho mínimo entre origem e destino.
    """
    if origem not in grafo.adjacencia or destino not in grafo.adjacencia:
        return inf, [], False
    
    dist, anterior, tem_ciclo_negativo = bellman_ford(grafo, origem)
    
    if tem_ciclo_negativo:
        return inf, [], True
    
    if dist[destino] == inf:
        return inf, [], False
    
    # Reconstrói o caminho
    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = anterior[atual]
    caminho.reverse()
    
    return dist[destino], caminho, False
