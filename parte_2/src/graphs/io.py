import pandas as pd
from .graph import Graph

def processar_dados_ufc(caminho_entrada: str, caminho_saida: str) -> None:
    """Processa dados brutos do UFC, calcula pesos e remove duplicatas."""
    df = pd.read_csv(caminho_entrada, sep=';', encoding='utf-8')
    
    colunas_necessarias = ['R_fighter', 'B_fighter', 'Fight_type', 'win_by', 'Winner']
    df_processado = df[colunas_necessarias].copy()
    df_processado = df_processado.dropna(subset=['R_fighter', 'B_fighter', 'Fight_type', 'win_by'])
    
    def calcular_peso(metodo_vitoria):
        metodo = str(metodo_vitoria).strip()
        if 'KO' in metodo or 'TKO' in metodo or 'Submission' in metodo:
            return 0.5
        elif 'Decision - Unanimous' in metodo or 'Unanimous' in metodo:
            return 2.0
        elif 'Decision - Split' in metodo or 'Split' in metodo or 'Decision - Majority' in metodo:
            return 3.0
        else:
            return 1.0
    
    df_processado['peso'] = df_processado['win_by'].apply(calcular_peso)
    df_processado['par_lutadores'] = df_processado.apply(
        lambda row: tuple(sorted([row['R_fighter'], row['B_fighter']])), 
        axis=1
    )
    df_processado = df_processado.sort_values('peso').groupby('par_lutadores', as_index=False).first()
    df_processado = df_processado.drop(columns=['par_lutadores'])
    df_processado.to_csv(caminho_saida, sep=';', index=False, encoding='utf-8')

def carregar_grafo_ufc(caminho_csv: str) -> Graph:
    """Carrega grafo de lutadores do UFC a partir do CSV processado."""
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8')
    grafo = Graph()
    
    for _, linha in df.iterrows():
        lutador_r = linha['R_fighter']
        lutador_b = linha['B_fighter']
        peso = linha['peso']
        vencedor = linha.get('Winner', None)
        
        grafo.adicionar_no(lutador_r)
        grafo.adicionar_no(lutador_b)
        grafo.adicionar_aresta(lutador_r, lutador_b, peso)
        
        if pd.notna(vencedor) and str(vencedor).strip() != '':
            vencedor_str = str(vencedor).strip()
            grafo.registrar_vitoria(vencedor_str)
    
    return grafo

if __name__ == "__main__":
    import os
    import sys
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parte2_dir = os.path.join(script_dir, '..', '..')
    data_dir = os.path.join(parte2_dir, 'data')
    
    caminho_entrada = os.path.join(data_dir, 'raw_total_fight_data.csv')
    caminho_saida = os.path.join(data_dir, 'total_fight_data_processado.csv')
    
    processar_dados_ufc(caminho_entrada, caminho_saida)