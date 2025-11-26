"""
Módulo para carregar e construir o grafo do dataset do Metro RER IDF (Paris).

O dataset contém estações de metrô/RER com suas conexões.
"""
import pandas as pd
import os
from math import sqrt
from typing import Dict, List, Tuple
from src.graphs.graph import Graph


def calcular_distancia_geografica(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância geográfica aproximada entre dois pontos (Haversine simplificado).
    Retorna distância em km.
    """
    # Fórmula simplificada para distâncias pequenas (Paris)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Aproximação: 1 grau ≈ 111 km
    return sqrt(dlat**2 + dlon**2) * 111.0


def carregar_grafo_metro(caminho_csv: str, usar_pesos_geograficos: bool = True) -> Graph:
    """
    Carrega o dataset do metro e constrói um grafo.
    
    Args:
        caminho_csv: caminho para o arquivo metro_rer_idf.csv
        usar_pesos_geograficos: se True, usa distância geográfica; se False, peso=1.0
    
    Retorna:
        Graph: grafo não dirigido com estações como nós e conexões como arestas
    """
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")
    
    df = pd.read_csv(caminho_csv)
    
    # Normaliza nomes de estações (remove espaços extras, padroniza)
    df['station'] = df['station'].str.strip()
    
    grafo = Graph()
    
    # Mapeia estação -> (linha, ordem, lat, lon)
    estacoes_info: Dict[str, Tuple[str, int, float, float]] = {}
    
    for _, row in df.iterrows():
        estacao = row['station']
        linha = row['ligne']
        ordem = int(row['ordre'])
        lat = float(row['latitude'])
        lon = float(row['longitude'])
        
        estacoes_info[estacao] = (linha, ordem, lat, lon)
        grafo.adicionar_no(estacao)
    
    # Constrói arestas:
    # 1. Conexões sequenciais na mesma linha
    linhas_estacoes: Dict[str, List[Tuple[str, int, float, float]]] = {}
    for estacao, (linha, ordem, lat, lon) in estacoes_info.items():
        if linha not in linhas_estacoes:
            linhas_estacoes[linha] = []
        linhas_estacoes[linha].append((estacao, ordem, lat, lon))
    
    # Ordena por ordem dentro de cada linha
    for linha in linhas_estacoes:
        linhas_estacoes[linha].sort(key=lambda x: x[1])
    
    # Adiciona arestas entre estações consecutivas na mesma linha
    for linha, estacoes_ordem in linhas_estacoes.items():
        for i in range(len(estacoes_ordem) - 1):
            est1, ord1, lat1, lon1 = estacoes_ordem[i]
            est2, ord2, lat2, lon2 = estacoes_ordem[i + 1]
            
            if usar_pesos_geograficos:
                peso = calcular_distancia_geografica(lat1, lon1, lat2, lon2)
            else:
                peso = 1.0
            
            grafo.adicionar_aresta(est1, est2, peso)
    
    # 2. Conexões por correspondências (mesma estação em linhas diferentes)
    # Estações com mesmo nome são a mesma estação física
    estacoes_por_nome: Dict[str, List[str]] = {}
    for estacao in estacoes_info.keys():
        nome_base = estacao  # Poderia normalizar mais (ex: remover sufixos)
        if nome_base not in estacoes_por_nome:
            estacoes_por_nome[nome_base] = []
        estacoes_por_nome[nome_base].append(estacao)
    
    # Conecta estações com mesmo nome (correspondências)
    for nome_base, lista_estacoes in estacoes_por_nome.items():
        if len(lista_estacoes) > 1:
            # Conecta todas as ocorrências da mesma estação
            for i in range(len(lista_estacoes)):
                for j in range(i + 1, len(lista_estacoes)):
                    est1 = lista_estacoes[i]
                    est2 = lista_estacoes[j]
                    # Peso baixo para correspondências (transbordo rápido)
                    peso_correspondencia = 0.1 if usar_pesos_geograficos else 1.0
                    grafo.adicionar_aresta(est1, est2, peso_correspondencia)
    
    return grafo


def obter_estatisticas_dataset(grafo: Graph) -> Dict:
    """
    Calcula estatísticas do dataset: |V|, |E|, tipo, distribuição de graus.
    
    Retorna:
        dict com estatísticas do grafo
    """
    nos = grafo.obter_nos()
    ordem = len(nos)
    tamanho = grafo.tamanho()
    densidade = grafo.densidade()
    
    # Distribuição de graus
    graus = [grafo.grau(no) for no in nos]
    grau_min = min(graus) if graus else 0
    grau_max = max(graus) if graus else 0
    grau_medio = sum(graus) / len(graus) if graus else 0
    
    # Histograma de graus
    from collections import Counter
    histograma_graus = dict(Counter(graus))
    
    return {
        'ordem': ordem,
        'tamanho': tamanho,
        'densidade': densidade,
        'tipo': 'não dirigido, ponderado',
        'grau_minimo': grau_min,
        'grau_maximo': grau_max,
        'grau_medio': round(grau_medio, 2),
        'distribuicao_graus': histograma_graus
    }

