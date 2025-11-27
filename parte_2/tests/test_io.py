from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT_DIR / "src"]
for dir_path in SRC_DIRS:
    if dir_path.exists():
        sys.path.insert(0, str(dir_path))

from graphs.io import processar_dados_ufc, carregar_grafo_ufc


def test_processar_dados_ufc_gera_csv_processado_sem_nulos(tmp_path):
    caminho_entrada = tmp_path / "raw.csv"
    caminho_saida = tmp_path / "processado.csv"

    df_raw = pd.DataFrame(
        [
            {
                "R_fighter": "A",
                "B_fighter": "B",
                "Fight_type": "Type1",
                "win_by": "KO",
                "Winner": "A",
                "Outro": 1,
            },
            {
                "R_fighter": "A",
                "B_fighter": "B",
                "Fight_type": "Type1",
                "win_by": "Decision - Unanimous",
                "Winner": "A",
                "Outro": 2,
            },
            {
                "R_fighter": "C",
                "B_fighter": "D",
                "Fight_type": "Type2",
                "win_by": "Decision - Split",
                "Winner": "C",
                "Outro": 3,
            },
            {
                "R_fighter": None,
                "B_fighter": "X",
                "Fight_type": "Type3",
                "win_by": "Submission",
                "Winner": "X",
                "Outro": 4,
            },
        ]
    )
    df_raw.to_csv(caminho_entrada, sep=";", index=False, encoding="utf-8")

    processar_dados_ufc(str(caminho_entrada), str(caminho_saida))

    assert caminho_saida.exists()

    df_proc = pd.read_csv(caminho_saida, sep=";", encoding="utf-8")
    assert set(["R_fighter", "B_fighter", "Fight_type", "win_by", "Winner", "peso"]) <= set(df_proc.columns)

    assert len(df_proc) == 2

    par_ab = df_proc[(df_proc["R_fighter"] == "A") & (df_proc["B_fighter"] == "B")]
    assert len(par_ab) == 1
    assert pytest.approx(0.5) == float(par_ab.iloc[0]["peso"])


def test_carregar_grafo_ufc_cria_nos_arestas_e_vitorias(tmp_path):
    caminho_csv = tmp_path / "processado.csv"

    df_proc = pd.DataFrame(
        [
            {
                "R_fighter": "A",
                "B_fighter": "B",
                "Fight_type": "Type1",
                "win_by": "KO",
                "Winner": "A",
                "peso": 0.5,
            },
            {
                "R_fighter": "B",
                "B_fighter": "C",
                "Fight_type": "Type1",
                "win_by": "Decision - Split",
                "Winner": "B",
                "peso": 3.0,
            },
        ]
    )
    df_proc.to_csv(caminho_csv, sep=";", index=False, encoding="utf-8")

    grafo = carregar_grafo_ufc(str(caminho_csv))

    nos = set(grafo.obter_nos())
    assert nos == {"A", "B", "C"}

    assert grafo.grau("A") == 1
    assert grafo.grau("B") == 2
    assert grafo.grau("C") == 1

    assert grafo.obter_vitorias("A") == 1
    assert grafo.obter_vitorias("B") == 1
