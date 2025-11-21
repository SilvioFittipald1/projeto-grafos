# src/graphs/algorithms.py
import heapq
from math import inf
from .graph import Graph


def dijkstra(grafo: Graph, origem: str, destino: str):
    """
    Algoritmo de Dijkstra para encontrar o caminho mínimo entre dois bairros.

    Retorna:
        custo_total (float) e caminho (lista de bairros, da origem ao destino).

    Se não houver caminho, retorna (inf, []).
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

        # Se pegamos uma entrada desatualizada, pula
        if dist_atual > dist[u]:
            continue

        # Se chegamos no destino, podemos parar
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

    # Reconstrói o caminho de trás pra frente: destino -> ... -> origem
    caminho = []
    atual = destino
    while atual != origem:
        caminho.append(atual)
        atual = anterior[atual]
    caminho.append(origem)
    caminho.reverse()  # agora origem -> ... -> destino

    return dist[destino], caminho
