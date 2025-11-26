# src/graphs/io.py
"""
Módulo de IO para a PARTE 1 (versão simples):
- Derreter o arquivo bairros_recife.csv em uma lista de bairros únicos,
  com a microrregião correspondente.

Saída esperada: um CSV com duas colunas:
    bairro, microrregiao

Observação importante sobre Setúbal:
- "Setúbal" não aparece como bairro no CSV (é sub-bairro de Boa Viagem).
- Para todas as tarefas que citam Setúbal, deve-se tratar como
  "Boa Viagem (Setúbal)" e considerar o nó "Boa Viagem" no grafo.
  (Esta função apenas derrete o CSV de microrregiões, então não
   faz nenhum tratamento especial aqui.)
"""

import pandas as pd
from .graph import Graph


def normalizar_bairro(nome: str) -> str:
   
    if not isinstance(nome, str):
        return nome

    nome = nome.strip()
    nome = " ".join(nome.split())
    return nome

def tratar_setubal(nome: str):
    """
    Aplica a regra especial para o bairro Setúbal.

    Retorna uma tupla (rotulo_saida, nome_no_grafo):

    - Se o nome se referir a Setúbal, então:
        rotulo_saida = "Boa Viagem (Setúbal)"
        nome_no_grafo = "Boa Viagem"

    - Caso contrário:
        rotulo_saida = nome normalizado
        nome_no_grafo = nome normalizado
    """
    if not isinstance(nome, str):
        # Se não for string, só devolve como está
        return nome, nome

    # Primeiro normaliza espaços
    nome_norm = normalizar_bairro(nome)
    # Compara em minúsculas para ser mais robusto
    nome_lower = nome_norm.lower()

    # Regra especial para Setúbal (com ou sem acento, com nome solto)
    if nome_lower == "setúbal" or nome_lower == "setubal":
        rotulo_saida = "Boa Viagem (Setúbal)"
        nome_no_grafo = "Boa Viagem"
        return rotulo_saida, nome_no_grafo

    # Caso geral: não é Setúbal
    return nome_norm, nome_norm


def carregar_grafo_bairros(caminho_bairros_unique: str) -> Graph:
    """
    Lê o arquivo bairros_unique.csv e cria um grafo
    onde cada nó é um bairro.

    Nesta etapa:
    - Não criamos arestas ainda, apenas os nós.
    - Cada nó é rotulado pelo nome do bairro (string).

    Retorna:
        grafo: instância de Graph com todos os bairros adicionados.
    """
    # 1) Lê o CSV com os bairros únicos
    df = pd.read_csv(caminho_bairros_unique)

    # 2) Garante que o arquivo tem as colunas esperadas
    colunas_necessarias = {"bairro", "microrregiao"}
    if not colunas_necessarias.issubset(df.columns):
        raise ValueError(
            "O arquivo bairros_unique.csv deve ter as colunas 'bairro' e 'microrregiao'."
        )

    # 3) Normaliza nomes de bairros
    df["bairro"] = df["bairro"].map(normalizar_bairro)

    # 4) Cria o grafo (não dirigido)
    grafo = Graph()  # seu grafo já é não dirigido

    # 5) Adiciona cada bairro como nó
    for bairro in df["bairro"]:
        grafo.adicionar_no(bairro)

    return grafo

def carregar_mapa_bairro_microrregiao(caminho_bairros_unique: str) -> dict:
    """
    Lê o arquivo bairros_unique.csv e devolve um dicionário:
        bairro -> microrregiao
    """
    df = pd.read_csv(caminho_bairros_unique)

    colunas_necessarias = {"bairro", "microrregiao"}
    if not colunas_necessarias.issubset(df.columns):
        raise ValueError(
            "O arquivo bairros_unique.csv deve ter as colunas 'bairro' e 'microrregiao'."
        )

    df["bairro"] = df["bairro"].map(normalizar_bairro)

    return dict(zip(df["bairro"], df["microrregiao"]))

def carregar_grafo_recife(
    caminho_bairros_unique: str,
    caminho_adjacencias: str
):
    """
    Monta o grafo completo dos bairros do Recife.

    - Usa bairros_unique.csv para saber quais são os bairros e suas microrregiões.
    - Usa o CSV de adjacências (montado por você) para adicionar as arestas.

    Retorna:
        grafo: Graph com nós + arestas
        bairro_para_microrregiao: dicionário bairro -> microrregiao
    """
    # 1) Carrega mapa bairro -> microrregiao
    bairro_para_microrregiao = carregar_mapa_bairro_microrregiao(caminho_bairros_unique)

    # 2) Cria o grafo e adiciona todos os bairros como nós
    grafo = Graph()
    for bairro in bairro_para_microrregiao.keys():
        grafo.adicionar_no(bairro)

    # 3) Lê o CSV de adjacências
    df_adj = pd.read_csv(caminho_adjacencias)
    
    df_adj.columns = df_adj.columns.str.strip()

    colunas_necessarias = {"bairro_origem", "bairro_destino", "peso"}
    if not colunas_necessarias.issubset(df_adj.columns):
        raise ValueError(

            f"O arquivo de adjacências deve ter as colunas "
            f"'bairro_origem', 'bairro_destino' e 'peso'. "
            f"Colunas encontradas: {list(df_adj.columns)}"
        )

    # 4) Normaliza nomes de bairros no CSV de adjacência
    df_adj["bairro_origem"] = df_adj["bairro_origem"].map(normalizar_bairro)
    df_adj["bairro_destino"] = df_adj["bairro_destino"].map(normalizar_bairro)

    # 5) Percorre as linhas e adiciona arestas
    for _, linha in df_adj.iterrows():
        origem = linha["bairro_origem"]
        destino = linha["bairro_destino"]

        # ignora linhas com bairros desconhecidos (por segurança)
        if origem not in bairro_para_microrregiao or destino not in bairro_para_microrregiao:
            continue

        peso = float(linha["peso"])

        grafo.adicionar_aresta(origem, destino, peso)

    return grafo, bairro_para_microrregiao


def derreter_bairros(caminho_entrada: str, caminho_saida: str) -> None:
 

    
    df = pd.read_csv(caminho_entrada)

   
    df_derretido = df.melt(
        var_name="microrregiao_coluna",
        value_name="bairro"
    )

   
    df_derretido = df_derretido.dropna(subset=["bairro"])

   
    df_derretido["microrregiao"] = (
        df_derretido["microrregiao_coluna"]
        .astype(str)
        .str.split(".")
        .str[0]
    )

    
    df_derretido["bairro"] = df_derretido["bairro"].map(normalizar_bairro)

   
    df_bairros_unicos = (
        df_derretido[["bairro", "microrregiao"]]
        .drop_duplicates()
        .sort_values(["microrregiao", "bairro"])
        .reset_index(drop=True)
    )

    df_bairros_unicos.to_csv(caminho_saida, index=False)

if __name__ == "__main__":
    derreter_bairros(
        "data/bairros_recife.csv",
        "data/bairros_unique.csv"
    )

