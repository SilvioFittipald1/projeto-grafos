import os
import json
import pandas as pd
from .graphs.io import carregar_grafo_ufc
from .graphs.graph import Graph

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out")

CAMINHO_UFC = os.path.join(DATA_DIR, "total_fight_data_processado.csv")

os.makedirs(OUT_DIR, exist_ok=True)

def calcular_metricas_globais(grafo: Graph) -> dict:
    return {
        "ordem": grafo.ordem(),
        "tamanho": grafo.tamanho(),
        "densidade": grafo.densidade(),
    }

def gerar_metricas_ufc():
    grafo = carregar_grafo_ufc(CAMINHO_UFC)

    metricas_globais = calcular_metricas_globais(grafo)
    with open(os.path.join(OUT_DIR, "ufc_global.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_globais, f, ensure_ascii=False, indent=2)


def gerar_ranking_vitorias():
    grafo = carregar_grafo_ufc(CAMINHO_UFC)

    todas_vitorias = grafo.obter_todas_vitorias()

    ranking = []
    for lutador, vitorias in todas_vitorias.items():
        ranking.append({
            "lutador": lutador,
            "vitorias": vitorias
        })
 
    ranking_ordenado = sorted(ranking, key=lambda x: x["vitorias"], reverse=True)

    with open(os.path.join(OUT_DIR, "ranking_vitorias.json"), "w", encoding="utf-8") as f:
        json.dump(ranking_ordenado, f, ensure_ascii=False, indent=2)


def gerar_ranking_lutas():
    grafo = carregar_grafo_ufc(CAMINHO_UFC)

    ranking = []
    for lutador in grafo.obter_nos():
        ranking.append({
            "lutador": lutador,
            "numero_lutas": grafo.grau(lutador)
        })

    ranking_ordenado = sorted(ranking, key=lambda x: x["numero_lutas"], reverse=True)

    with open(os.path.join(OUT_DIR, "ranking_lutas.json"), "w", encoding="utf-8") as f:
        json.dump(ranking_ordenado, f, ensure_ascii=False, indent=2)


def gerar_descricao_dataset():
    grafo = carregar_grafo_ufc(CAMINHO_UFC)
    
    ordem = grafo.ordem()
    tamanho = grafo.tamanho()
    densidade = grafo.densidade()
    
    graus = []
    for lutador in grafo.obter_nos():
        graus.append(grafo.grau(lutador))
    
    graus_df = pd.Series(graus)
    grau_min = graus_df.min()
    grau_max = graus_df.max()
    grau_medio = graus_df.mean()
    grau_mediana = graus_df.median()
    grau_desvio = graus_df.std()
    
    faixas = {
        "1-5 lutas": len([g for g in graus if 1 <= g <= 5]),
        "6-10 lutas": len([g for g in graus if 6 <= g <= 10]),
        "11-15 lutas": len([g for g in graus if 11 <= g <= 15]),
        "16-20 lutas": len([g for g in graus if 16 <= g <= 20]),
        "21+ lutas": len([g for g in graus if g >= 21])
    }
    conteudo = f"""
1. INFORMAÇÕES DO GRAFO

|V| (Ordem - Número de Vértices): {ordem}
|E| (Tamanho - Número de Arestas): {tamanho}

Tipo de Grafo:
  - Dirigido: NÃO
  - Ponderado: SIM
  - Descrição: Grafo não-dirigido ponderado

Cada vértice representa um lutador do UFC.
Cada aresta representa uma luta entre dois lutadores.
O peso das arestas indica a importância/tipo da vitória:
  - Nocaute/Submissão: peso 4.0
  - Decisão Unânime: peso 2.0
  - Decisão Dividida/Majoritária: peso 3.0
  - Outros: peso 1.0

2. DENSIDADE DO GRAFO

Densidade: {densidade:.6f}

A densidade indica o quão conectado está o grafo. Um valor próximo de 0
indica que poucos lutadores enfrentaram-se mutuamente, enquanto um valor
próximo de 1 indicaria que quase todos os lutadores já lutaram entre si.

3. DISTRIBUIÇÃO DE GRAUS

Estatísticas Descritivas:
  - Grau Mínimo: {grau_min}
  - Grau Máximo: {grau_max}
  - Grau Médio: {grau_medio:.2f}
  - Grau Mediana: {grau_mediana:.2f}
  - Desvio Padrão: {grau_desvio:.2f}

O grau de um vértice representa o número de lutas que o lutador participou.

Distribuição por Faixas:
  - {faixas['1-5 lutas']:4d} lutadores com 1-5 lutas ({faixas['1-5 lutas']/ordem*100:5.1f}%)
  - {faixas['6-10 lutas']:4d} lutadores com 6-10 lutas ({faixas['6-10 lutas']/ordem*100:5.1f}%)
  - {faixas['11-15 lutas']:4d} lutadores com 11-15 lutas ({faixas['11-15 lutas']/ordem*100:5.1f}%)
  - {faixas['16-20 lutas']:4d} lutadores com 16-20 lutas ({faixas['16-20 lutas']/ordem*100:5.1f}%)
  - {faixas['21+ lutas']:4d} lutadores com 21+ lutas ({faixas['21+ lutas']/ordem*100:5.1f}%)

4. INTERPRETAÇÃO

A distribuição de graus mostra que a maioria dos lutadores tem poucas lutas
registradas no dataset, enquanto alguns lutadores veteranos possuem um número
significativamente maior de lutas. Isso é típico de redes do mundo real, onde
poucos nós são altamente conectados (hubs) e a maioria tem poucas conexões.

O histograma visual da distribuição de graus pode ser encontrado em:
  - distribuicao_graus.png
"""
    
    caminho_saida = os.path.join(OUT_DIR, "descricao_dataset.txt")
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo)


if __name__ == "__main__":
    gerar_metricas_ufc()
    gerar_ranking_vitorias()
    gerar_ranking_lutas()
    gerar_descricao_dataset()
