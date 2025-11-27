# Projeto de Teoria dos Grafos

## Descrição Geral

Este projeto implementa e aplica algoritmos clássicos de Teoria dos Grafos em dois contextos distintos: análise de conectividade entre bairros do Recife (Parte 1) e análise de rede de lutadores do UFC (Parte 2). O trabalho abrange desde a implementação de estruturas de dados fundamentais até a geração de visualizações interativas e análises estatísticas detalhadas.

## Estrutura do Projeto

```
projeto-grafos/
├── parte_1/              # Análise dos bairros do Recife
│   ├── data/             # Dados de entrada (bairros, adjacências, endereços)
│   ├── src/              # Código-fonte
│   │   ├── graphs/       # Implementação de grafos e algoritmos
│   │   ├── solve.py      # Script principal de análise
│   │   └── viz.py        # Geração de visualizações HTML
│   ├── out/              # Resultados (JSON, CSV, HTML, PNG)
│   └── tests/            # Testes automatizados
│
├── parte_2/              # Análise da rede de lutadores do UFC
│   ├── data/             # Dados de entrada (lutas do UFC)
│   ├── src/              # Código-fonte
│   │   ├── graphs/       # Implementação de grafos e algoritmos
│   │   ├── solve.py      # Script principal de análise
│   │   └── viz.py        # Geração de visualizações HTML
│   ├── out/              # Resultados (JSON, HTML, relatórios)
│   └── tests/            # Testes automatizados
│
├── main_app.py           # Interface Streamlit para visualização
├── requirements.txt      # Dependências do projeto
└── README.md             # Este arquivo
```

## Parte 1: Análise dos Bairros do Recife

### Implementação

**Estrutura de Dados:**
- Grafo não-dirigido com lista de adjacência
- Suporte a pesos nas arestas
- Operações: adicionar nós/arestas, obter vizinhos, calcular grau, densidade, subgrafo induzido

**Algoritmos Implementados:**
- **BFS (Busca em Largura):** Exploração por níveis, árvore de busca, caminhos mínimos não-ponderados
- **DFS (Busca em Profundidade):** Exploração recursiva, árvore de busca, detecção de ciclos, classificação de arestas
- **Dijkstra:** Caminhos mínimos com pesos não-negativos usando heap de prioridade
- **Bellman-Ford:** Caminhos mínimos com suporte a pesos negativos e detecção de ciclos negativos

### Dados de Entrada

- `bairros_unique.csv`: Lista de bairros com suas microrregiões
- `adjacencias_bairros.csv`: Arestas entre bairros adjacentes
- `enderecos.csv`: Pares de endereços para cálculo de rotas

### Saídas Geradas

**Métricas Estruturais:**
- `recife_global.json`: Ordem, tamanho e densidade do grafo completo
- `microrregioes.json`: Métricas por microrregião (subgrafos induzidos)
- `graus.csv`: Ranking de bairros por número de conexões
- `densidades.csv`: Ranking de bairros por densidade de ego-rede
- `ego_bairro.csv`: Estatísticas detalhadas de ego-redes

**Caminhos Mínimos:**
- `distancias_enderecos.csv`: Rotas entre pares de endereços com custo e caminho completo
- `nova_descoberta_setubal.json`: Análise detalhada de rota específica

**Visualizações Interativas:**
- `arvore_percurso.html`: Árvore DFS hierárquica
- `mapa_graus.html`: Heatmap de graus dos bairros
- `arvore_bfs_boaviagem.html`: Árvore BFS a partir de Boa Viagem
- `grafo_interativo.html`: Grafo completo com controles de busca e caminhos
- `distribuicao_graus.png`: Histograma da distribuição de graus
- `ranking_densidade_ego_microrregiao.png`: Gráfico de barras de densidades

### Como Executar (Parte 1)

1. Navegue até o diretório da Parte 1:
```bash
cd parte_1
```

2. Processe os dados de entrada (se necessário):
```bash
python -m src.graphs.io
```

3. Execute o script principal de análise:
```bash
python -m src.solve
```

4. Execute o script de visualizações:
```bash
python -m src.viz
```

5. Execute os testes automatizados:
```bash
python -m pytest tests/
```

## Parte 2: Análise da Rede de Lutadores do UFC

### Implementação

**Modelagem do Grafo:**
- Vértices: Lutadores do UFC
- Arestas: Lutas realizadas entre dois lutadores
- Pesos: Baseados no tipo de vitória
  - KO/TKO/Submission: 0.5 (vitória decisiva)
  - Decisão Unânime: 2.0
  - Decisão Dividida/Majoritária: 3.0
  - Outros: 1.0

**Algoritmos Aplicados:**
- BFS para exploração de componentes conexas
- DFS para classificação de arestas e detecção de ciclos
- Dijkstra para caminhos mínimos entre lutadores
- Bellman-Ford testado com grafos sintéticos (pesos negativos e ciclos negativos)

### Dados de Entrada

- `raw_total_fight_data.csv`: Dados brutos de lutas do UFC
- `total_fight_data_processado.csv`: Dados processados com pesos calculados

### Saídas Geradas

**Métricas e Análises:**
- `ufc_global.json`: Ordem, tamanho e densidade do grafo
- `ranking_vitorias.json`: Ranking de lutadores por número de vitórias
- `ranking_lutas.json`: Ranking de lutadores por número de lutas
- `descricao_dataset.txt`: Análise estatística completa do dataset
- `parte2_report.json`: Métricas de desempenho dos algoritmos (tempo e memória)

**Visualizações HTML:**
- `grafo_interativo.html`: Grafo completo com heatmap de vitórias, busca de lutadores, cálculo de caminhos e filtro por categoria de peso
- `parte2_bfs.html`: Resultados de BFS a partir de lutadores mais conectados
- `parte2_dfs.html`: Resultados de DFS com classificação de arestas
- `parte2_dijkstra.html`: Caminhos mínimos calculados com Dijkstra
- `parte2_bellman_ford.html`: Testes do Bellman-Ford em grafos sintéticos

**Gráficos:**
- `distribuicao_graus.png`: Histograma da distribuição de lutas por lutador

### Como Executar (Parte 2)

1. Navegue até o diretório da Parte 2:
```bash
cd parte_2
```

2. Processe os dados de entrada (se necessário):
```bash
python -m src.graphs.io
```

3. Execute o script principal de análise:
```bash
python -m src.solve
```

4. Execute o script de visualizações:
```bash
python -m src.viz
```

5. Execute os testes automatizados:
```bash
python -m pytest tests/
```

## Interface de Visualização (Streamlit)

O projeto inclui uma interface web interativa desenvolvida com Streamlit que permite visualizar todas as saídas HTML geradas pelas duas partes do projeto.

### Como Executar

No diretório raiz do projeto:

```bash
streamlit run main_app.py
```

A interface será aberta automaticamente no navegador e permite:
- Navegar entre Parte 1 e Parte 2
- Selecionar diferentes visualizações através de dropdown
- Visualizar grafos interativos, árvores de busca e análises de caminhos

## Instalação e Configuração

### Requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone ou baixe o repositório do projeto

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Dependências

- **pytest**: Framework de testes automatizados
- **pandas**: Manipulação e análise de dados
- **matplotlib**: Geração de gráficos estáticos
- **seaborn**: Visualizações estatísticas avançadas
- **pyvis**: Geração de grafos interativos em HTML
- **streamlit**: Interface web para visualização

## Testes Automatizados

O projeto inclui suítes completas de testes para validar a corretude dos algoritmos implementados.

### Parte 1 - Testes Disponíveis

**BFS (test_bfs.py):**
- Construção correta da árvore de busca
- Cálculo de níveis e pais
- Tratamento de origens inválidas
- Caminhos mínimos entre pares de vértices
- Casos especiais (origem = destino, destinos inalcançáveis)

**DFS (test_dfs.py):**
- Construção da árvore de busca
- Ordem de descoberta dos vértices
- Tratamento de origens inválidas
- Existência de caminhos entre pares
- Detecção de vértices isolados

**Dijkstra (test_dijkstra.py):**
- Cálculo correto de custos mínimos
- Reconstrução de caminhos
- Tratamento de vértices inexistentes
- Destinos inalcançáveis
- Caso origem = destino

**Bellman-Ford (test_bellman_ford.py):**
- Caminhos mínimos com pesos positivos
- Suporte a pesos negativos
- Detecção de ciclos negativos
- Tratamento de origens inválidas
- Destinos inalcançáveis

### Parte 2 - Testes Disponíveis

Testes similares aos da Parte 1, adaptados para o contexto do grafo de lutadores do UFC, incluindo validações específicas para pesos baseados em tipos de vitória.

### Executar Todos os Testes

```bash
python -m pytest
```

### Executar Testes Específicos

```bash
python -m pytest parte_1/tests/test_dijkstra.py
python -m pytest parte_2/tests/test_bfs.py
```

## Análise de Desempenho

A Parte 2 inclui medição automática de desempenho dos algoritmos, registrando:
- Tempo de execução (em milissegundos)
- Uso de memória (em kilobytes)
- Dataset utilizado
- Tarefa específica executada

Os resultados são salvos em `parte_2/out/parte2_report.json` e podem ser analisados para comparar a eficiência dos diferentes algoritmos.

## Discussão Crítica

O arquivo `parte_2/out/discussao critica.txt` contém uma análise detalhada sobre:
- Escolha da modelagem do grafo
- Justificativa dos pesos atribuídos
- Limitações da abordagem
- Considerações sobre arestas simétricas
- Aplicabilidade do Bellman-Ford no contexto do UFC
- Testes com grafos sintéticos para validação

## Autores

- Bernardo Heuer
- Silvio Fittipaldi
- Rodrigo Nunes
- Eduardo Roma

## Observações Importantes

1. Os dados de entrada devem estar nos diretórios `parte_1/data/` e `parte_2/data/` antes da execução
2. As visualizações HTML são geradas automaticamente e podem ser abertas em qualquer navegador moderno
3. O grafo interativo da Parte 2 inclui funcionalidades avançadas como busca de lutadores, cálculo de caminhos mínimos e filtro por categoria de peso
4. Os testes automatizados garantem a corretude das implementações e devem ser executados após qualquer modificação no código
5. A interface Streamlit facilita a navegação entre as diferentes visualizações sem necessidade de abrir arquivos HTML manualmente
