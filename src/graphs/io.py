import csv
import os
import unicodedata

def load_csv(filepath):
    """Lê o arquivo CSV original e retorna cabeçalho e matriz de dados."""
    with open(filepath, encoding="utf-8") as f:
        reader = list(csv.reader(f))
        cabecalho = reader[0]   # nomes das microrregiões (ex: 1.1, 1.2, ...)
        matriz = reader[1:]     # nomes dos bairros por coluna
    return cabecalho, matriz

def normalize_name(name):
    """Remove acentos e padroniza para formato título."""
    name = name.strip()
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
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

def salvar_bairros(bairros_dict, saida=os.path.join("out", "bairros_unique.csv")):
    """Salva o resultado (bairro, microrregiao) em CSV na pasta out."""
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["bairro", "microrregiao"])
        for bairro, microrregiao in sorted(bairros_dict.items()):
            writer.writerow([bairro, microrregiao])
    
    print(f"✅ Arquivo '{saida}' gerado com {len(bairros_dict)} bairros únicos.")

if __name__ == "__main__":
    entrada = os.path.join("data", "bairros_recife.csv")
    cabecalho, matriz = load_csv(entrada)
    bairros_dict = validate_csv(cabecalho, matriz)
    salvar_bairros(bairros_dict)
