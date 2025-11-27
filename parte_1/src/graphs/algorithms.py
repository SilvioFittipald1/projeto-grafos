import heapq
from math import inf
from .graph import Graph
from collections import deque


def _validar_pesos_nao_negativos(grafo: Graph):
    """Valida se todos os pesos do grafo são não-negativos."""
    for u in grafo.obter_nos():
        for _v, peso in grafo.vizinhos(u):
            if float(peso) < 0:
                raise ValueError("Dijkstra não aceita pesos negativos.")


def dijkstra(grafo: Graph, origem: str, destino: str):
    """Encontra o caminho mínimo entre origem e destino usando Dijkstra."""
    if origem not in grafo.adjacencia or destino not in grafo.adjacencia:
        return inf, []

    _validar_pesos_nao_negativos(grafo)

    dist = {no: inf for no in grafo.obter_nos()}
    dist[origem] = 0.0
    anterior = {}
    fila = [(0.0, origem)]

    while fila:
        dist_atual, u = heapq.heappop(fila)

        if dist_atual > dist[u]:
            continue

        if u == destino:
            break

        for v, peso in grafo.vizinhos(u):
            novo_custo = dist[u] + float(peso)
            if novo_custo < dist[v]:
                dist[v] = novo_custo
                anterior[v] = u
                heapq.heappush(fila, (novo_custo, v))

    if dist[destino] == inf:
        return inf, []

    caminho = []
    atual = destino
    while atual != origem:
        caminho.append(atual)
        atual = anterior[atual]
    caminho.append(origem)
    caminho.reverse()

    return dist[destino], caminho


def bfs_arvore(grafo: Graph, origem: str):
    """Constrói a árvore BFS a partir da origem."""
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
    """Encontra o menor caminho entre origem e destino usando BFS."""
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
    
    caminho = []
    no_atual = destino
    while no_atual is not None:
        caminho.append(no_atual)
        no_atual = anterior[no_atual]
    
    caminho.reverse()
    return caminho


def dfs_arvore(grafo: Graph, origem: str):
    """Constrói a árvore DFS a partir da origem."""
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
    """Encontra um caminho entre origem e destino usando DFS."""
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


def dfs_detectar_ciclo(grafo: Graph) -> bool:
    """Detecta se o grafo possui ciclos."""
    visitado = set()

    def dfs(u, pai):
        visitado.add(u)
        for v, _ in grafo.vizinhos(u):
            if v == pai:
                continue
            if v not in visitado:
                if dfs(v, u):
                    return True
            else:
                return True
        return False

    for no in grafo.obter_nos():
        if no not in visitado and dfs(no, None):
            return True
    return False


def dfs_classificar_arestas(grafo: Graph):
    """Classifica as arestas do grafo em tree, back ou cross."""
    visitado = set()
    em_processamento = set()
    classificacao = {}

    def registrar(u, v, tipo):
        chave = tuple(sorted((u, v)))
        if chave not in classificacao:
            classificacao[chave] = tipo

    def dfs(u, pai):
        visitado.add(u)
        em_processamento.add(u)

        for v, _ in grafo.vizinhos(u):
            if v == pai:
                continue
            if v not in visitado:
                registrar(u, v, "tree")
                dfs(v, u)
            elif v in em_processamento:
                registrar(u, v, "back")
            else:
                registrar(u, v, "cross")

        em_processamento.remove(u)

    for no in grafo.obter_nos():
        if no not in visitado:
            dfs(no, None)

    return classificacao


def bellman_ford(grafo: Graph, origem: str):
    """Encontra caminhos mínimos a partir da origem e detecta ciclos negativos."""
    if origem not in grafo.adjacencia:
        raise ValueError(f"Bairro de origem '{origem}' não existe no grafo.")
    
    nos = list(grafo.obter_nos())
    dist = {no: inf for no in nos}
    anterior = {no: None for no in nos}
    dist[origem] = 0.0
    
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
        
        if not houve_mudanca:
            break
    
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
    """Encontra o caminho mínimo entre origem e destino usando Bellman-Ford."""
    if origem not in grafo.adjacencia or destino not in grafo.adjacencia:
        return inf, [], False
    
    dist, anterior, tem_ciclo_negativo = bellman_ford(grafo, origem)
    
    if tem_ciclo_negativo:
        return inf, [], True
    
    if dist[destino] == inf:
        return inf, [], False
    
    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = anterior[atual]
    caminho.reverse()
    
    return dist[destino], caminho, False
