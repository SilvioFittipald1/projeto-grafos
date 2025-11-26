"""
Script principal para executar comparações de algoritmos na Parte 2.

Executa BFS, DFS, Dijkstra e Bellman-Ford e gera relatório de desempenho.
"""
import os
import sys
import json
import time
from typing import Dict, List, Tuple, Any
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graphs.graph import Graph
from src.graphs.algorithms import (
    bfs_arvore, dfs_arvore, dijkstra, bellman_ford, bellman_ford_caminho
)
from parte2.io import carregar_grafo_metro, obter_estatisticas_dataset


def medir_tempo(func, *args, **kwargs):
    """Mede o tempo de execução de uma função."""
    inicio = time.perf_counter()
    resultado = func(*args, **kwargs)
    fim = time.perf_counter()
    tempo_segundos = fim - inicio
    return resultado, tempo_segundos


def executar_bfs_multiplas_fontes(grafo: Graph, fontes: List[str]) -> List[Dict]:
    """
    Executa BFS a partir de múltiplas fontes.
    
    Retorna lista de resultados com ordem, camadas, etc.
    """
    resultados = []
    
    for origem in fontes:
        if origem not in grafo.obter_nos():
            print(f"Aviso: estação '{origem}' não encontrada no grafo.")
            continue
        
        (pai, nivel), tempo_exec = medir_tempo(bfs_arvore, grafo, origem)
        
        # Estatísticas
        nos_visitados = len(pai)
        niveis = list(nivel.values())
        nivel_max = max(niveis) if niveis else 0
        
        # Conta nós por nível
        nos_por_nivel = {}
        for no, nv in nivel.items():
            nos_por_nivel[nv] = nos_por_nivel.get(nv, 0) + 1
        
        resultados.append({
            'origem': origem,
            'nos_visitados': nos_visitados,
            'nivel_maximo': nivel_max,
            'nos_por_nivel': nos_por_nivel,
            'tempo_segundos': round(tempo_exec, 6)
        })
    
    return resultados


def executar_dfs_multiplas_fontes(grafo: Graph, fontes: List[str]) -> List[Dict]:
    """
    Executa DFS a partir de múltiplas fontes.
    
    Retorna lista de resultados com ordem, ciclos detectados, etc.
    """
    resultados = []
    
    for origem in fontes:
        if origem not in grafo.obter_nos():
            print(f"Aviso: estação '{origem}' não encontrada no grafo.")
            continue
        
        (pai, descoberta), tempo_exec = medir_tempo(dfs_arvore, grafo, origem)
        
        # Estatísticas
        nos_visitados = len(pai)
        ordem_descoberta = sorted(descoberta.items(), key=lambda x: x[1])
        
        resultados.append({
            'origem': origem,
            'nos_visitados': nos_visitados,
            'ordem_descoberta': [no for no, _ in ordem_descoberta[:10]],  # Primeiros 10
            'tempo_segundos': round(tempo_exec, 6)
        })
    
    return resultados


def executar_dijkstra_multiplos_pares(grafo: Graph, pares: List[Tuple[str, str]]) -> List[Dict]:
    """
    Executa Dijkstra para múltiplos pares origem-destino.
    
    Retorna lista de resultados com custo, caminho, tempo.
    """
    resultados = []
    
    for origem, destino in pares:
        if origem not in grafo.obter_nos() or destino not in grafo.obter_nos():
            print(f"Aviso: par ({origem}, {destino}) contém estação não encontrada.")
            continue
        
        (custo, caminho), tempo = medir_tempo(dijkstra, grafo, origem, destino)
        
        resultados.append({
            'origem': origem,
            'destino': destino,
            'custo': custo if custo != float('inf') else None,
            'tamanho_caminho': len(caminho),
            'caminho': caminho[:5] + ['...'] + caminho[-5:] if len(caminho) > 10 else caminho,
            'tempo_segundos': round(tempo, 6)
        })
    
    return resultados


def executar_bellman_ford_casos(grafo: Graph, casos: List[Dict]) -> List[Dict]:
    """
    Executa Bellman-Ford para casos com e sem ciclo negativo.
    
    casos: lista de dicts com 'origem', 'destino' (opcional), 'grafo' (opcional, para casos especiais)
    """
    resultados = []
    
    for caso in casos:
        # Se o caso tem um grafo específico (para teste de ciclo negativo)
        if 'grafo' in caso:
            grafo_teste = caso['grafo']
        else:
            grafo_teste = grafo
        
        origem = caso['origem']
        destino = caso.get('destino')
        
        if origem not in grafo_teste.obter_nos():
            print(f"Aviso: origem '{origem}' não encontrada no grafo de teste.")
            continue
        
        if destino:
            (custo, caminho, tem_ciclo), tempo = medir_tempo(
                bellman_ford_caminho, grafo_teste, origem, destino
            )
            resultados.append({
                'origem': origem,
                'destino': destino,
                'custo': custo if custo != float('inf') else None,
                'tem_ciclo_negativo': tem_ciclo,
                'tamanho_caminho': len(caminho) if caminho else 0,
                'tempo_segundos': round(tempo, 6),
                'tipo': 'com_destino'
            })
        else:
            (dist, anterior, tem_ciclo), tempo = medir_tempo(
                bellman_ford, grafo_teste, origem
            )
            resultados.append({
                'origem': origem,
                'tem_ciclo_negativo': tem_ciclo,
                'nos_alcancaveis': sum(1 for d in dist.values() if d != float('inf')),
                'tempo_segundos': round(tempo, 6),
                'tipo': 'sem_destino'
            })
    
    return resultados


def gerar_relatorio_completo(
    grafo: Graph,
    caminho_saida: str,
    fontes_bfs_dfs: List[str] = None,
    pares_dijkstra: List[Tuple[str, str]] = None,
    casos_bellman_ford: List[Dict] = None
) -> Dict:
    """
    Gera relatório completo de comparação de algoritmos.
    
    Args:
        grafo: grafo a ser analisado
        caminho_saida: caminho para salvar out/parte2_report.json
        fontes_bfs_dfs: lista de estações para BFS/DFS (padrão: 3 aleatórias)
        pares_dijkstra: lista de (origem, destino) para Dijkstra (padrão: 5 aleatórios)
        casos_bellman_ford: lista de casos para Bellman-Ford
    """
    nos = grafo.obter_nos()
    
    # Valores padrão
    if fontes_bfs_dfs is None:
        import random
        random.seed(42)
        fontes_bfs_dfs = random.sample(nos, min(3, len(nos)))
    
    if pares_dijkstra is None:
        import random
        random.seed(42)
        pares_dijkstra = [
            (random.choice(nos), random.choice(nos))
            for _ in range(min(5, len(nos)))
        ]
        # Remove pares iguais
        pares_dijkstra = [(o, d) for o, d in pares_dijkstra if o != d]
    
    if casos_bellman_ford is None:
        # Caso 1: normal (sem ciclo negativo)
        origem1 = fontes_bfs_dfs[0] if fontes_bfs_dfs else nos[0]
        destino1 = pares_dijkstra[0][1] if pares_dijkstra else nos[-1]
        
        # Caso 2: com ciclo negativo (cria um grafo pequeno com ciclo negativo garantido)
        from src.graphs.graph import Graph
        grafo_ciclo = Graph()
        # Cria um triângulo com ciclo negativo: A->B->C->A
        grafo_ciclo.adicionar_aresta('TESTE_A', 'TESTE_B', 1.0)
        grafo_ciclo.adicionar_aresta('TESTE_B', 'TESTE_C', -3.0)  # Peso negativo
        grafo_ciclo.adicionar_aresta('TESTE_C', 'TESTE_A', -1.0)  # Peso negativo
        # Ciclo: 1 + (-3) + (-1) = -3 (ciclo negativo)
        
        casos_bellman_ford = [
            {'origem': origem1, 'destino': destino1, 'tipo': 'sem_ciclo_negativo'},
            {
                'grafo': grafo_ciclo,
                'origem': 'TESTE_A',
                'destino': 'TESTE_C',
                'tipo': 'com_ciclo_negativo'
            }
        ]
    
    # Estatísticas do dataset
    print("Calculando estatísticas do dataset...")
    stats_dataset = obter_estatisticas_dataset(grafo)
    
    # BFS
    print("Executando BFS...")
    resultados_bfs, tempo_bfs_total = medir_tempo(
        executar_bfs_multiplas_fontes, grafo, fontes_bfs_dfs
    )
    
    # DFS
    print("Executando DFS...")
    resultados_dfs, tempo_dfs_total = medir_tempo(
        executar_dfs_multiplas_fontes, grafo, fontes_bfs_dfs
    )
    
    # Dijkstra
    print("Executando Dijkstra...")
    resultados_dijkstra, tempo_dijkstra_total = medir_tempo(
        executar_dijkstra_multiplos_pares, grafo, pares_dijkstra
    )
    
    # Bellman-Ford
    print("Executando Bellman-Ford...")
    resultados_bf, tempo_bf_total = medir_tempo(
        executar_bellman_ford_casos, grafo, casos_bellman_ford
    )
    
    # Monta relatório
    relatorio = {
        'dataset': stats_dataset,
        'bfs': {
            'tempo_total_segundos': round(tempo_bfs_total, 6),
            'resultados': resultados_bfs
        },
        'dfs': {
            'tempo_total_segundos': round(tempo_dfs_total, 6),
            'resultados': resultados_dfs
        },
        'dijkstra': {
            'tempo_total_segundos': round(tempo_dijkstra_total, 6),
            'resultados': resultados_dijkstra
        },
        'bellman_ford': {
            'tempo_total_segundos': round(tempo_bf_total, 6),
            'resultados': resultados_bf
        },
        'resumo_desempenho': {
            'bfs_tempo_medio': round(tempo_bfs_total / len(resultados_bfs), 6) if resultados_bfs else 0,
            'dfs_tempo_medio': round(tempo_dfs_total / len(resultados_dfs), 6) if resultados_dfs else 0,
            'dijkstra_tempo_medio': round(tempo_dijkstra_total / len(resultados_dijkstra), 6) if resultados_dijkstra else 0,
            'bellman_ford_tempo_medio': round(tempo_bf_total / len(resultados_bf), 6) if resultados_bf else 0
        }
    }
    
    # Salva relatório (garante que vai para parte2/out/ se não especificado)
    if not os.path.isabs(caminho_saida) and not caminho_saida.startswith('out/'):
        # Se não é caminho absoluto e não começa com out/, coloca em parte2/out/
        caminho_saida = str(Path(__file__).parent / 'out' / Path(caminho_saida).name)
    
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\nRelatório salvo em: {caminho_saida}")
    print(f"\nResumo:")
    print(f"  Dataset: {stats_dataset['ordem']} nós, {stats_dataset['tamanho']} arestas")
    print(f"  BFS: {len(resultados_bfs)} execuções, tempo médio: {relatorio['resumo_desempenho']['bfs_tempo_medio']:.6f}s")
    print(f"  DFS: {len(resultados_dfs)} execuções, tempo médio: {relatorio['resumo_desempenho']['dfs_tempo_medio']:.6f}s")
    print(f"  Dijkstra: {len(resultados_dijkstra)} execuções, tempo médio: {relatorio['resumo_desempenho']['dijkstra_tempo_medio']:.6f}s")
    print(f"  Bellman-Ford: {len(resultados_bf)} execuções, tempo médio: {relatorio['resumo_desempenho']['bellman_ford_tempo_medio']:.6f}s")
    
    return relatorio


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comparação de algoritmos - Parte 2')
    parser.add_argument('--dataset', type=str, default='parte2/metro_rer_idf.csv',
                        help='Caminho para o dataset CSV')
    parser.add_argument('--out', type=str, default='parte2/out/parte2_report.json',
                        help='Caminho de saída para o relatório JSON')
    parser.add_argument('--pesos-geograficos', action='store_true',
                        help='Usar pesos geográficos (distância real)')
    
    args = parser.parse_args()
    
    # Carrega grafo
    print(f"Carregando dataset: {args.dataset}")
    grafo = carregar_grafo_metro(args.dataset, usar_pesos_geograficos=args.pesos_geograficos)
    print(f"Grafo carregado: {grafo.ordem()} nós, {grafo.tamanho()} arestas")
    
    # Gera relatório
    gerar_relatorio_completo(grafo, args.out)


if __name__ == '__main__':
    main()

