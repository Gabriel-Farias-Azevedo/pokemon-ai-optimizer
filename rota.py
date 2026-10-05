import heapq
from mapa import obter_custo_movimento, DIFICULDADE_GINASIOS

def obter_vizinhos(mapa, x, y):
    vizinhos = []
    movimentos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    linhas = len(mapa)
    colunas = len(mapa[0])
    
    for dx, dy in movimentos:
        nx, ny = x + dx, y + dy
        if 0 <= nx < linhas and 0 <= ny < colunas:
            vizinhos.append((nx, ny))

    return vizinhos


def dijkstra_todos_destinos(mapa, origem, destinos):
    fila = [(0, origem)]
    custos = {origem: 0}
    anteriores = {origem: None}
    restantes = set(destinos.values())
    restantes.discard(origem)

    caminhos = {}
    custos_destinos = {}

    while fila and restantes:
        custo_atual, atual = heapq.heappop(fila)

        if atual in restantes:
            restantes.remove(atual)

        for vizinho in obter_vizinhos(mapa, *atual):
            custo = custo_atual + obter_custo_movimento(mapa[vizinho[0]][vizinho[1]])

            if vizinho not in custos or custo < custos[vizinho]:
                custos[vizinho] = custo
                anteriores[vizinho] = atual
                heapq.heappush(fila, (custo, vizinho))

    for nome, destino in destinos.items():
        if destino == origem or destino not in custos:
            continue

        caminho = []
        atual = destino

        while atual is not None:
            caminho.append(atual)
            atual = anteriores.get(atual)

        caminho.reverse()
        caminhos[nome] = caminho
        custos_destinos[nome] = custos[destino]

    return custos_destinos, caminhos


def mapear_coordenadas_ginasios(mapa):
    coordenadas = {}

    for i, linha in enumerate(mapa):
        for j, celula in enumerate(linha):
            if celula in DIFICULDADE_GINASIOS:
                coordenadas[celula] = (i, j)

    return coordenadas


def gerar_matriz_distancias(mapa, inicio, destino):
    coordenadas_ginasios = mapear_coordenadas_ginasios(mapa)
    pontos = {'1': inicio, 'U': destino, **coordenadas_ginasios}

    custos = {}
    caminhos = {}

    print(f"Pré-calculando distâncias entre {len(pontos)} pontos...")

    for origem, coordenada in pontos.items():
        custos_origem, caminhos_origem = dijkstra_todos_destinos(mapa, coordenada, pontos)

        for destino, custo in custos_origem.items():
            custos[(origem, destino)] = custo
            caminhos[(origem, destino)] = caminhos_origem[destino]

    print("Pré-cálculo concluído!")

    return custos, caminhos, list(coordenadas_ginasios.keys())


def reconstruir_rota_completa(ordem_ginasios, tabela_caminhos):
    pontos = ['1'] + ordem_ginasios + ['U']
    rota = []

    for i in range(len(pontos) - 1):
        origem = pontos[i]
        destino = pontos[i + 1]
        trecho = tabela_caminhos[(origem, destino)]

        if i == 0:
            rota.extend(trecho)
        else:
            rota.extend(trecho[1:])

    return rota


