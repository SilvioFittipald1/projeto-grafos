# Projeto Grafos

Implementação de algoritmos de grafos para análise dos bairros do Recife, com foco em métricas estruturais e rotas mínimas.

## Visão Geral

- `parte1/src/graphs/graph.py`: define um grafo não dirigido usando lista de adjacência com utilitários como grau, densidade e subgrafo induzido.
- `parte1/src/graphs/algorithms.py`: reúne algoritmos clássicos (BFS/DFS, Dijkstra e Bellman-Ford) já prontos para reutilização.
- `parte1/src/graphs/io.py`: normaliza os nomes de bairros, trata o caso especial de Setúbal e carrega dados dos CSVs fornecidos.
- `parte1/src/solve.py`: orquestra as etapas principais do trabalho, gerando métricas globais, recortes por microrregião, ego-redes e distâncias entre pares de bairros.
- `tests/`: contém os testes automatizados (atualmente focados no Bellman-Ford) escritos com `pytest`.

## Fluxo Principal (`parte1/src/solve.py`)

1. **`passo_3()`**
   - Lê os dados de `data/bairros_unique.csv` e `data/adjacencias_bairros.csv`.
   - Calcula ordem/tamanho/densidade do grafo completo (`out/recife_global.json`).
   - Gera métricas por microrregião (`out/microrregioes.json`) com subgrafos induzidos.
   - Exporta estatísticas de ego-redes por bairro (`out/ego_bairro.csv`).

2. **`passo_4()`**
   - Reutiliza `ego_bairro.csv` para montar rankings de graus (`out/graus.csv`) e densidades (`out/densidades.csv`).

3. **`passo_6()`**
   - Usa `data/enderecos.csv` para calcular caminhos mínimos entre pares de bairros com Dijkstra.
   - Salva `out/distancias_enderecos.csv` com custo e percurso em texto; o par "Nova Descoberta" → "Setúbal" também pode ser exportado em JSON.

## Requisitos e Configuração

1. Instale o Python 3.10+.
2. (Opcional) Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como Executar

No diretório raiz do projeto:

```bash
python -m parte1.src.solve
```

O script garante a criação da pasta `out/` e sobrescreve os arquivos mencionados no fluxo principal. Ajuste os CSVs em `parte1/data/` conforme necessário antes da execução.

## Testes Automatizados

Os testes vivem na pasta `tests/` e usam `pytest`.

- Bellman-Ford: valida caminhos mínimos, origens inválidas, ciclos negativos e destinos inalcançáveis.
  ```bash
  python -m pytest tests/test_bellman_ford.py
  ```
- BFS: cobre geração da árvore (pais/níveis), erro para origem inexistente e caminhos mínimos entre pares (incluindo origem = destino e destinos isolados).
  ```bash
  python -m pytest tests/test_bfs.py
  ```
- DFS: verifica construção da árvore de busca (pais e ordem de descoberta), erro com origem inválida e caminhos possíveis/impossíveis entre pares.
  ```bash
  python -m pytest tests/test_dfs.py
  ```
- Dijkstra: assegura custo mínimo, casos de nós inexistentes (origem/destino), destinos inalcançáveis e origem = destino.
  ```bash
  python -m pytest tests/test_dijkstra.py
  ```

Use `python -m pytest` para rodar toda a suíte quando outros testes forem adicionados.
