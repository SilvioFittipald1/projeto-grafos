import csv
import os
import unicodedata
import pandas as pd

def load_csv(filepath):
    """Lê o arquivo CSV original e retorna cabeçalho e matriz de dados."""
    df = pd.read_csv(filepath, encoding='utf-8')
    cabecalho = list(df.columns)
    # transforma DataFrame em lista de listas (linhas)
    matriz = df.fillna("").astype(str).values.tolist()
    return cabecalho, matriz

def normalize_name(name):
    """Padroniza o nome: remove espaços extras e aplica Title Case mantendo acentuação.

    Observação: não removemos acentuação para preservar nomes reais (ex.: "Boa Viagem").
    """
    if name is None:
        return ""
    name = name.strip()
    # Normaliza para forma composta (NFC) para manter acentos consistentes
    name = unicodedata.normalize("NFC", name)
    # Converte múltiplos espaços em um só
    name = " ".join(name.split())
    return name.title()

def validate_csv(cabecalho, matriz):
    """
    'Derrete' o CSV: transforma colunas (microrregiões) em linhas únicas de bairros.
    Retorna um dicionário {bairro_normalizado: microrregiao}.
    """
    bairros_dict = {}

    for col_idx, microrregiao in enumerate(cabecalho):
        for linha in matriz:
            if len(linha) <= col_idx:
                continue
            bairro = linha[col_idx].strip()
            if not bairro:
                continue

            bairro_norm = normalize_name(bairro)
            # Evita duplicatas: mantém apenas a primeira microrregião encontrada
            if bairro_norm not in bairros_dict:
                bairros_dict[bairro_norm] = microrregiao

    return bairros_dict

def salvar_bairros(bairros_dict, saida=os.path.join("data", "bairros_unique.csv")):
    """Salva o resultado (bairro, microrregiao) em CSV na pasta data.

    A especificação da Parte 1 exige que `bairros_unique.csv` fique dentro da
    pasta `data/`.
    """
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["bairro", "microrregiao"])
        for bairro, microrregiao in sorted(bairros_dict.items()):
            writer.writerow([bairro, microrregiao])

    print(f"✅ Arquivo '{saida}' gerado com {len(bairros_dict)} bairros únicos.")


def load_adjacencias(filepath=os.path.join("data", "adjacencias_bairros.csv")):
    """Carrega o CSV de adjacências (arestas).

    Formato esperado (com cabeçalho ou sem):
    bairro_origem,bairro_destino,logradouro,observacao,peso

    Linhas vazias ou que comecem com '#' são ignoradas.
    Retorna lista de tuplas: (origem, destino, logradouro, observacao, peso)
    """
    arestas = []
    if not os.path.exists(filepath):
        print(f"⚠️  Arquivo de adjacências não encontrado: {filepath}")
        return arestas

    df = pd.read_csv(filepath, comment='#', encoding='utf-8')
    cols = [c for c in df.columns]
    for _, row in df.iterrows():
        origem = str(row.get(cols[0], '')).strip() if len(cols) > 0 else ''
        destino = str(row.get(cols[1], '')).strip() if len(cols) > 1 else ''
        logradouro = str(row.get(cols[2], '')).strip() if len(cols) > 2 else ''
        observacao = str(row.get(cols[3], '')).strip() if len(cols) > 3 else ''
        peso = row.get(cols[4], '') if len(cols) > 4 else ''
        if not origem or not destino:
            continue
        origem = normalize_name(origem)
        destino = normalize_name(destino)
        if origem.lower() in ("setúbal", "setubal"):
            origem = "Boa Viagem (Setúbal)"
        if destino.lower() in ("setúbal", "setubal"):
            destino = "Boa Viagem (Setúbal)"
        try:
            peso_val = float(peso) if peso != '' and pd.notna(peso) else 1.0
        except Exception:
            peso_val = 1.0
        arestas.append((origem, destino, logradouro, observacao, peso_val))

    return arestas

if __name__ == "__main__":
    entrada = os.path.join("data", "bairros_recife.csv")
    cabecalho, matriz = load_csv(entrada)
    bairros_dict = validate_csv(cabecalho, matriz)
    salvar_bairros(bairros_dict)
