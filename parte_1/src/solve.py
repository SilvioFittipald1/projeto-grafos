import os
import json
import pandas as pd
from graphs.io import carregar_grafo_recife, tratar_setubal 
from graphs.graph import Graph
from graphs.algorithms import dijkstra

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "out", "parte1")

CAMINHO_BAIRROS_UNIQUE = os.path.join(DATA_DIR, "bairros_unique.csv")
CAMINHO_ADJACENCIAS = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

os.makedirs(OUT_DIR, exist_ok=True)

def calcular_metricas_globais(grafo: Graph) -> dict:
    """Calcula ordem, tamanho e densidade do grafo completo."""
    return {
        "ordem": grafo.ordem(),
        "tamanho": grafo.tamanho(),
        "densidade": grafo.densidade()
    }

def calcular_metricas_microrregioes(grafo: Graph, bairro_para_micro: dict):
    """Calcula ordem, tamanho e densidade para cada microrregião."""
    microrregioes = sorted(set(bairro_para_micro.values()))
    resultados = []

    for micro in microrregioes:
        bairros_micro = [b for b, m in bairro_para_micro.items() if m == micro]
        sub = grafo.subgrafo_induzido(bairros_micro)

        resultados.append({
            "microrregiao": micro,
            "ordem": sub.ordem(),
            "tamanho": sub.tamanho(),
            "densidade": sub.densidade()
        })

    return resultados

def calcular_ego_por_bairro(grafo: Graph):
    """Calcula métricas da ego-subrede para cada bairro."""
    linhas = []

    for bairro in grafo.obter_nos():
        vizinhos = [v for (v, _) in grafo.vizinhos(bairro)]
        nos_ego = [bairro] + vizinhos

        ego = grafo.subgrafo_induzido(nos_ego)

        linha = {
            "bairro": bairro,
            "grau": grafo.grau(bairro),
            "ordem_ego": ego.ordem(),
            "tamanho_ego": ego.tamanho(),
            "densidade_ego": ego.densidade()
        }
        linhas.append(linha)

    return linhas

def passo_3():
    """Gera métricas globais, por microrregião e ego-subrede."""
    grafo, bairro_para_micro = carregar_grafo_recife(
        CAMINHO_BAIRROS_UNIQUE,
        CAMINHO_ADJACENCIAS
    )

    metricas_globais = calcular_metricas_globais(grafo)
    with open(os.path.join(OUT_DIR, "recife_global.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_globais, f, ensure_ascii=False, indent=2)

    metricas_micros = calcular_metricas_microrregioes(grafo, bairro_para_micro)
    with open(os.path.join(OUT_DIR, "microrregioes.json"), "w", encoding="utf-8") as f:
        json.dump(metricas_micros, f, ensure_ascii=False, indent=2)

    ego_linhas = calcular_ego_por_bairro(grafo)
    df_ego = pd.DataFrame(ego_linhas)
    df_ego.to_csv(os.path.join(OUT_DIR, "ego_bairro.csv"), index=False)

def passo_4():
    """Gera rankings de graus e densidades ego."""
    caminho_ego = os.path.join(OUT_DIR, "ego_bairro.csv")
    caminho_graus = os.path.join(OUT_DIR, "graus.csv")
    caminho_densidades = os.path.join(OUT_DIR, "densidades.csv")

    df = pd.read_csv(caminho_ego)

    df_graus = df[["bairro", "grau"]].copy()
    df_graus = df_graus.sort_values(by="grau", ascending=False)
    df_graus.to_csv(caminho_graus, index=False)

    df_den = df[["bairro", "densidade_ego"]].copy()
    df_den = df_den.sort_values(by="densidade_ego", ascending=False)
    df_den.to_csv(caminho_densidades, index=False)

def passo_6():
    """Calcula distâncias entre pares de bairros usando Dijkstra."""
    caminho_enderecos = os.path.join(DATA_DIR, "enderecos.csv")
    caminho_bairros_unique = os.path.join(DATA_DIR, "bairros_unique.csv")
    caminho_adjacencias = os.path.join(DATA_DIR, "adjacencias_bairros.csv")

    caminho_saida_csv = os.path.join(OUT_DIR, "distancias_enderecos.csv")
    caminho_saida_json_nd_setubal = os.path.join(
        OUT_DIR, "percurso_nova_descoberta_setubal.json"
    )

    os.makedirs(OUT_DIR, exist_ok=True)

    grafo, _ = carregar_grafo_recife(
        caminho_bairros_unique,
        caminho_adjacencias
    )

    df_end = pd.read_csv(caminho_enderecos)

    colunas_necessarias = {"bairro_X", "bairro_Y"}
    if not colunas_necessarias.issubset(df_end.columns):
        raise ValueError(
            "O arquivo enderecos.csv deve ter as colunas 'bairro_X' e 'bairro_Y'."
        )

    linhas_saida = []
    info_nd_setubal = None

    for _, linha in df_end.iterrows():
        bairro_X_raw = linha["bairro_X"]
        bairro_Y_raw = linha["bairro_Y"]

        rotulo_X, no_X = tratar_setubal(bairro_X_raw)
        rotulo_Y, no_Y = tratar_setubal(bairro_Y_raw)

        X = rotulo_X
        Y = rotulo_Y

        custo, caminho = dijkstra(grafo, no_X, no_Y)
        caminho_str = " > ".join(caminho) if caminho else ""

        linhas_saida.append({
            "X": X,
            "Y": Y,
            "bairro_X": rotulo_X,
            "bairro_Y": rotulo_Y,
            "custo": custo,
            "caminho": caminho_str
        })
        
        if no_X == "Nova Descoberta" and "Setúbal" in bairro_Y_raw:
            info_nd_setubal = {
                "origem": rotulo_X,
                "destino": rotulo_Y,
                "custo": custo,
                "caminho": caminho
            }

    df_saida = pd.DataFrame(linhas_saida)
    df_saida.to_csv(caminho_saida_csv, index=False)


    if info_nd_setubal is not None:
        with open(caminho_saida_json_nd_setubal, "w", encoding="utf-8") as f:
            json.dump(info_nd_setubal, f, ensure_ascii=False, indent=2)


def gerar_descricao_dataset():
    """Gera arquivo .txt com descrição completa do dataset conforme requisitos do projeto."""
    grafo, bairro_para_micro = carregar_grafo_recife(
        CAMINHO_BAIRROS_UNIQUE,
        CAMINHO_ADJACENCIAS
    )
    
    # Coleta informações básicas
    ordem = grafo.ordem()  # |V|
    tamanho = grafo.tamanho()  # |E|
    densidade = grafo.densidade()
    
    # Coleta distribuição de graus
    graus = []
    for bairro in grafo.obter_nos():
        graus.append(grafo.grau(bairro))
    
    graus_df = pd.Series(graus)
    grau_min = graus_df.min()
    grau_max = graus_df.max()
    grau_medio = graus_df.mean()
    grau_mediana = graus_df.median()
    grau_desvio = graus_df.std()
    
    # Distribuição por faixas
    faixas = {
        "1-3 conexões": len([g for g in graus if 1 <= g <= 3]),
        "4-6 conexões": len([g for g in graus if 4 <= g <= 6]),
        "7-9 conexões": len([g for g in graus if 7 <= g <= 9]),
        "10-12 conexões": len([g for g in graus if 10 <= g <= 12]),
        "13+ conexões": len([g for g in graus if g >= 13])
    }
    
    # Informações sobre microrregiões
    microrregioes = sorted(set(bairro_para_micro.values()))
    num_microrregioes = len(microrregioes)
    
    # Gera o conteúdo do arquivo
    conteudo = f"""
1. INFORMAÇÕES DO GRAFO

|V| (Ordem - Número de Vértices): {ordem}
|E| (Tamanho - Número de Arestas): {tamanho}

Tipo de Grafo:
  - Dirigido: NÃO
  - Ponderado: NÃO
  - Descrição: Grafo não-dirigido simples

Cada vértice representa um bairro do Recife.
Cada aresta representa uma adjacência geográfica entre dois bairros.
O dataset contém {num_microrregioes} microrregiões administrativas.

2. DENSIDADE DO GRAFO

Densidade: {densidade:.6f}

A densidade indica o quão conectado está o grafo. Um valor próximo de 0
indica que poucos bairros são adjacentes entre si, enquanto um valor
próximo de 1 indicaria que quase todos os bairros são adjacentes.

3. DISTRIBUIÇÃO DE GRAUS

Estatísticas Descritivas:
  - Grau Mínimo: {grau_min}
  - Grau Máximo: {grau_max}
  - Grau Médio: {grau_medio:.2f}
  - Grau Mediana: {grau_mediana:.2f}
  - Desvio Padrão: {grau_desvio:.2f}

O grau de um vértice representa o número de bairros adjacentes.

Distribuição por Faixas:
  - {faixas['1-3 conexões']:4d} bairros com 1-3 conexões ({faixas['1-3 conexões']/ordem*100:5.1f}%)
  - {faixas['4-6 conexões']:4d} bairros com 4-6 conexões ({faixas['4-6 conexões']/ordem*100:5.1f}%)
  - {faixas['7-9 conexões']:4d} bairros com 7-9 conexões ({faixas['7-9 conexões']/ordem*100:5.1f}%)
  - {faixas['10-12 conexões']:4d} bairros com 10-12 conexões ({faixas['10-12 conexões']/ordem*100:5.1f}%)
  - {faixas['13+ conexões']:4d} bairros com 13+ conexões ({faixas['13+ conexões']/ordem*100:5.1f}%)

4. INTERPRETAÇÃO

A distribuição de graus mostra como os bairros do Recife estão conectados
geograficamente. Bairros com maior grau são aqueles que fazem fronteira com
muitos outros bairros, geralmente localizados em regiões centrais. Bairros
com menor grau tendem a estar em regiões periféricas ou costeiras.

O histograma visual da distribuição de graus pode ser encontrado em:
  - distribuicao_graus.png

Dados detalhados dos graus por bairro estão disponíveis em:
  - graus.csv
  - ego_bairro.csv

Informações sobre microrregiões estão disponíveis em:
  - microrregioes.json
"""
    
    # Salva o arquivo
    caminho_saida = os.path.join(OUT_DIR, "descricao_dataset.txt")
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo)


if __name__ == "__main__":
    passo_3()
    passo_4()
    passo_6()
    gerar_descricao_dataset()
