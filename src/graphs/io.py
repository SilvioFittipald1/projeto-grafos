import pandas as pd
from .graph import Graph


def normalizar_bairro(nome: str) -> str:
    """Normaliza o nome de um bairro removendo espaços extras."""
    if not isinstance(nome, str):
        return nome

    nome = nome.strip()
    nome = " ".join(nome.split())
    return nome

def tratar_setubal(nome: str):
    """Aplica regra especial para Setúbal, retornando (rótulo, nó_grafo)."""
    if not isinstance(nome, str):
        return nome, nome

    nome_norm = normalizar_bairro(nome)
    nome_lower = nome_norm.lower()

    if nome_lower == "setúbal" or nome_lower == "setubal":
        rotulo_saida = "Boa Viagem (Setúbal)"
        nome_no_grafo = "Boa Viagem"
        return rotulo_saida, nome_no_grafo

    return nome_norm, nome_norm


def carregar_grafo_bairros(caminho_bairros_unique: str) -> Graph:
    """Carrega grafo com nós de bairros a partir do CSV."""
    df = pd.read_csv(caminho_bairros_unique)

    colunas_necessarias = {"bairro", "microrregiao"}
    if not colunas_necessarias.issubset(df.columns):
        raise ValueError(
            "O arquivo bairros_unique.csv deve ter as colunas 'bairro' e 'microrregiao'."
        )

    df["bairro"] = df["bairro"].map(normalizar_bairro)
    grafo = Graph()

    for bairro in df["bairro"]:
        grafo.adicionar_no(bairro)

    return grafo

def carregar_mapa_bairro_microrregiao(caminho_bairros_unique: str) -> dict:
    """Retorna dicionário mapeando bairro para microrregião."""
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
    """Carrega grafo completo com nós e arestas dos bairros do Recife."""
    bairro_para_microrregiao = carregar_mapa_bairro_microrregiao(caminho_bairros_unique)

    grafo = Graph()
    for bairro in bairro_para_microrregiao.keys():
        grafo.adicionar_no(bairro)

    df_adj = pd.read_csv(caminho_adjacencias)
    df_adj.columns = df_adj.columns.str.strip()

    colunas_necessarias = {"bairro_origem", "bairro_destino", "peso"}
    if not colunas_necessarias.issubset(df_adj.columns):
        raise ValueError(
            f"O arquivo de adjacências deve ter as colunas "
            f"'bairro_origem', 'bairro_destino' e 'peso'. "
            f"Colunas encontradas: {list(df_adj.columns)}"
        )

    df_adj["bairro_origem"] = df_adj["bairro_origem"].map(normalizar_bairro)
    df_adj["bairro_destino"] = df_adj["bairro_destino"].map(normalizar_bairro)

    for _, linha in df_adj.iterrows():
        origem = linha["bairro_origem"]
        destino = linha["bairro_destino"]

        if origem not in bairro_para_microrregiao or destino not in bairro_para_microrregiao:
            continue

        peso = float(linha["peso"])
        grafo.adicionar_aresta(origem, destino, peso)

    return grafo, bairro_para_microrregiao


def derreter_bairros(caminho_entrada: str, caminho_saida: str) -> None:
    """Derrete CSV de microrregiões em lista de bairros únicos."""
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

