def solve():
    """Gera as saídas da Parte 1 usando apenas os nós (bairros).

    Se `data/adjacencias_bairros.csv` não estiver disponível, o grafo será
    construído apenas com nós e todas as métricas que dependem de arestas
    serão calculadas considerando 0 arestas.
    """
    import os
    import csv
    import json
    from graphs import io as io_mod
    from graphs import graph as graph_mod

    os.makedirs("out", exist_ok=True)

    # Carrega bairros únicos
    bairros_path = os.path.join("data", "bairros_unique.csv")
    bairros = {}
    if os.path.exists(bairros_path):
        with open(bairros_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                b = r.get("bairro", "").strip()
                m = r.get("microrregiao", "").strip()
                if b:
                    bairros[b] = m
    else:
        print(f"⚠️  Arquivo {bairros_path} não encontrado. Rode src/graphs/io.py primeiro.")
        return

    # Monta grafo com nós apenas
    G = graph_mod.Graph()
    for b, m in bairros.items():
        G.add_node(b, microrregiao=m)

    # Tenta carregar adjacências (pode estar ausente)
    arestas = io_mod.load_adjacencias(os.path.join("data", "adjacencias_bairros.csv"))
    for o, d, log, obs, peso in arestas:
        G.add_edge(o, d, peso=peso, logradouro=log, observacao=obs)

    # Métricas globais
    ordem = G.number_of_nodes()
    tamanho = G.number_of_edges()

    def densidade(n_nodes, n_edges):
        if n_nodes < 2:
            return 0.0
        return (2.0 * n_edges) / (n_nodes * (n_nodes - 1))

    dens = densidade(ordem, tamanho)

    recife_global = {"ordem": ordem, "tamanho": tamanho, "densidade": dens}
    with open(os.path.join("out", "recife_global.json"), "w", encoding="utf-8") as f:
        json.dump(recife_global, f, indent=2, ensure_ascii=False)

    # Métricas por microrregião
    micros = {}
    for b, m in bairros.items():
        micros.setdefault(m, set()).add(b)

    micror_list = []
    for m, nodes in micros.items():
        nodes = set(nodes)
        n_nodes = len(nodes)
        # conta arestas cujo ambos extremos estão em `nodes`
        n_edges = 0
        for u, v, _ in G.edges():
            if u in nodes and v in nodes:
                n_edges += 1
        micr = {"microrregiao": m, "ordem": n_nodes, "tamanho": n_edges, "densidade": densidade(n_nodes, n_edges)}
        micror_list.append(micr)

    with open(os.path.join("out", "microrregioes.json"), "w", encoding="utf-8") as f:
        json.dump(micror_list, f, indent=2, ensure_ascii=False)

    # Ego-networks e graus
    ego_rows = []
    graus = []
    for v in sorted(G.nodes()):
        grau = G.degree(v)
        viz = set(G.neighbors(v))
        ego_nodes = set(viz) | {v}
        ordem_ego = len(ego_nodes)
        # conta arestas no subgrafo induzido por ego_nodes
        ecount = 0
        for a in ego_nodes:
            for b in G.neighbors(a):
                if b in ego_nodes:
                    # cada aresta contada duas vezes
                    ecount += 1
        tamanho_ego = ecount // 2
        dens_ego = densidade(ordem_ego, tamanho_ego)
        ego_rows.append({"bairro": v, "grau": grau, "ordem_ego": ordem_ego, "tamanho_ego": tamanho_ego, "densidade_ego": dens_ego})
        graus.append((v, grau))

    # salva ego_bairro.csv
    with open(os.path.join("out", "ego_bairro.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"])
        for r in ego_rows:
            writer.writerow([r['bairro'], r['grau'], r['ordem_ego'], r['tamanho_ego'], r['densidade_ego']])

    # salva graus.csv
    with open(os.path.join("out", "graus.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["bairro", "grau"])
        for b, g in sorted(graus, key=lambda x: (-x[1], x[0])):
            writer.writerow([b, g])

    # Determina bairro com maior densidade_ego e maior grau
    bairro_mais_denso = max(ego_rows, key=lambda x: x['densidade_ego'])['bairro'] if ego_rows else None
    bairro_maior_grau = max(graus, key=lambda x: x[1])[0] if graus else None

    print("Resumo:")
    print(f"Ordem: {ordem}, Tamanho: {tamanho}, Densidade: {dens:.6f}")
    print(f"Bairro com maior densidade_ego: {bairro_mais_denso}")
    print(f"Bairro com maior grau: {bairro_maior_grau}")

    # Endereços e distâncias
    enderecos_path = os.path.join("data", "enderecos.csv")
    if not os.path.exists(enderecos_path):
        # cria um CSV com 5 pares exemplo (bairros conhecidos no arquivo gerado)
        sample = [
            ("Avenida Conselheiro Aguiar, Boa Viagem", "Rua Real, Nova Descoberta", "Boa Viagem", "Nova Descoberta"),
            ("Rua do Sol, Boa Vista", "Rua X, Coelhos", "Boa Vista", "Coelhos"),
            ("Praça Y, Pina", "Rua Z, Ipsep", "Pina", "Ipsep"),
            ("Av. Domingos Ferreira, Imbiribeira", "Rua W, Ipsep", "Imbiribeira", "Ipsep"),
            ("Rua A, Nova Descoberta", "Rua B, Setúbal", "Nova Descoberta", "Setúbal"),
        ]
        os.makedirs(os.path.dirname(enderecos_path), exist_ok=True)
        with open(enderecos_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["X", "Y", "bairro_X", "bairro_Y"])
            for x, y, bx, by in sample:
                writer.writerow([x, y, bx, by])

    # lê endereços e calcula Dijkstra pelos bairros
    dist_out_rows = []
    with open(os.path.join("data", "enderecos.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            X = r.get("X", "")
            Y = r.get("Y", "")
            bX = r.get("bairro_X", "").strip()
            bY = r.get("bairro_Y", "").strip()
            # normaliza Setúbal para Boa Viagem
            if bX.lower() in ("setúbal", "setubal"):
                bX = "Boa Viagem"
            if bY.lower() in ("setúbal", "setubal"):
                bY = "Boa Viagem"

            dist, prev = __import__("graphs.algorithms", fromlist=["dijkstra"]).dijkstra(G, bX)
            custo = dist.get(bY, float('inf'))
            # reconstrói caminho
            path = []
            if custo != float('inf'):
                cur = bY
                while cur is not None:
                    path.append(cur)
                    cur = prev.get(cur)
                path = list(reversed(path))
            dist_out_rows.append({"X": X, "Y": Y, "bairro_X": bX, "bairro_Y": bY, "custo": custo, "caminho": path})

    # salva distancias_enderecos.csv
    with open(os.path.join("out", "distancias_enderecos.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["X", "Y", "bairro_X", "bairro_Y", "custo", "caminho"])
        for r in dist_out_rows:
            writer.writerow([r['X'], r['Y'], r['bairro_X'], r['bairro_Y'], r['custo'], ";".join(r['caminho'])])

    # salva percurso obrigatório Nova Descoberta -> Setúbal
    target_path = os.path.join("out", "percurso_nova_descoberta_setubal.json")
    # tenta reconstruir o caminho que calculamos (pode ser vazio)
    for r in dist_out_rows:
        if r['bairro_X'].lower() == 'nova descoberta' and r['bairro_Y'].lower() in ('setúbal', 'setubal', 'boa viagem'):
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(r, f, ensure_ascii=False, indent=2)
            break

    print(f"Arquivos gerados em 'out/' (recife_global.json, microrregioes.json, ego_bairro.csv, graus.csv, distancias_enderecos.csv, percurso_nova_descoberta_setubal.json se aplicável).")


if __name__ == "__main__":
    solve()

if __name__ == "__main__":
    solve()