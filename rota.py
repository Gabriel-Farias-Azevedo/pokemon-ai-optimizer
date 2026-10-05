import heapq
from mapa import obter_custo_movimento, DIFICULDADE_GINASIOS

QTD_GINASIOS_CHAVE = 16


def obter_vizinhos(mapa, linha, coluna):
    vizinhos = []
    movimentos = [(0, 1), (1, 0), (0, -1), (-1, 0)]  
    total_linhas = len(mapa)
    total_colunas = len(mapa[0])

    for mov_linha, mov_coluna in movimentos:
        nova_linha = linha + mov_linha
        nova_coluna = coluna + mov_coluna

        if 0 <= nova_linha < total_linhas and 0 <= nova_coluna < total_colunas:
            vizinhos.append((nova_linha, nova_coluna))

    return vizinhos


def distancia_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_estrela_mapa(mapa, origem, destino):
    fronteira = [(distancia_manhattan(origem, destino), 0, origem)]
    custos = {origem: 0}
    anteriores = {origem: None}
    visitados = set()

    while len(fronteira) > 0:
        f, custo_atual, atual = heapq.heappop(fronteira)

        if atual in visitados:
            continue
        visitados.add(atual)

        if atual == destino:
            break

        linha, coluna = atual
        for vizinho in obter_vizinhos(mapa, linha, coluna):
            terreno = mapa[vizinho[0]][vizinho[1]]
            custo = custo_atual + obter_custo_movimento(terreno)

            if vizinho not in custos or custo < custos[vizinho]:
                custos[vizinho] = custo
                anteriores[vizinho] = atual
                f = custo + distancia_manhattan(vizinho, destino)
                heapq.heappush(fronteira, (f, custo, vizinho))

    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = anteriores[atual]
    caminho.reverse()

    nos_fronteira = set()
    for f, custo, posicao in fronteira:
        if posicao not in visitados:
            nos_fronteira.add(posicao)

    return custos[destino], caminho, visitados, nos_fronteira


def mapear_coordenadas_ginasios(mapa):
    coordenadas = {}

    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if mapa[i][j] in DIFICULDADE_GINASIOS:
                coordenadas[mapa[i][j]] = (i, j)

    return coordenadas


def gerar_matriz_distancias(mapa, inicio, destino):
    coordenadas_ginasios = mapear_coordenadas_ginasios(mapa)

    pontos = {}
    pontos['1'] = inicio
    pontos['U'] = destino
    for ginasio in coordenadas_ginasios:
        pontos[ginasio] = coordenadas_ginasios[ginasio]

    nomes = list(pontos)
    custos = {}
    caminhos = {}

    print(f"Calculando distâncias entre {len(pontos)} pontos com A*...")

    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            a = nomes[i]
            b = nomes[j]
            custo, caminho, visitados, fronteira = a_estrela_mapa(mapa, pontos[a], pontos[b])

            custos[(a, b)] = custo
            custos[(b, a)] = custo
            caminhos[(a, b)] = caminho
            caminhos[(b, a)] = list(reversed(caminho))

    print("Distâncias calculadas!")

    ginasios = list(coordenadas_ginasios)
    return custos, caminhos, ginasios

def esta_no_conjunto(conjunto, i):
    return (conjunto & (1 << i)) != 0


def colocar_no_conjunto(conjunto, i):
    return conjunto | (1 << i)


def tirar_do_conjunto(conjunto, i):
    return conjunto & ~(1 << i)


def escolher_ginasios_chave(ginasios, custos, quantidade):
    pontos = ginasios + ['1', 'U']
    isolamento = {}

    for g in ginasios:
        distancias = []
        for outro in pontos:
            if outro != g:
                distancias.append(custos[(g, outro)])
        distancias.sort()
        isolamento[g] = distancias[0] + distancias[1]

    escolhidos = []
    for _ in range(quantidade):
        mais_isolado = None
        for g in ginasios:
            if g in escolhidos:
                continue
            if mais_isolado is None or isolamento[g] > isolamento[mais_isolado]:
                mais_isolado = g
        escolhidos.append(mais_isolado)

    return escolhidos


def montar_tabela_heuristica(chave, custos):
    k = len(chave)
    total_grupos = 2 ** k

    tabela = []
    for _ in range(total_grupos):
        tabela.append([0] * k)

    for grupo in range(total_grupos):
        for i in range(k):
            if esta_no_conjunto(grupo, i):
                continue

            if grupo == 0:
                tabela[grupo][i] = custos[(chave[i], 'U')]
                continue

            melhor = float('inf')
            for j in range(k):
                if esta_no_conjunto(grupo, j):
                    resto = tirar_do_conjunto(grupo, j)
                    custo = custos[(chave[i], chave[j])] + tabela[resto][j]
                    if custo < melhor:
                        melhor = custo
            tabela[grupo][i] = melhor

    return tabela


def calcular_heuristica(atual, visitados, chave, posicoes_chave, tabela, custos):
    faltam = 0
    for j in range(len(chave)):
        if not esta_no_conjunto(visitados, posicoes_chave[j]):
            faltam = colocar_no_conjunto(faltam, j)

    if faltam == 0:
        return custos[(atual, 'U')]

    melhor = float('inf')
    for j in range(len(chave)):
        if esta_no_conjunto(faltam, j):
            resto = tirar_do_conjunto(faltam, j)
            custo = custos[(atual, chave[j])] + tabela[resto][j]
            if custo < melhor:
                melhor = custo

    return melhor


def a_estrela_ginasios(ginasios, custos):
    n = len(ginasios)
    todos = 2 ** n - 1

    chave = escolher_ginasios_chave(ginasios, custos, QTD_GINASIOS_CHAVE)
    tabela = montar_tabela_heuristica(chave, custos)

    posicoes_chave = []
    for g in chave:
        posicoes_chave.append(ginasios.index(g))

    inicio = ('1', 0)
    melhor_g = {inicio: 0}
    anteriores = {inicio: None}
    h_inicio = calcular_heuristica('1', 0, chave, posicoes_chave, tabela, custos)
    fronteira = [(h_inicio, 0, '1', 0)]
    expandidos = 0

    while len(fronteira) > 0:
        f, g, atual, visitados = heapq.heappop(fronteira)

        if atual == 'U':
            break

        if g > melhor_g[(atual, visitados)]:
            continue

        expandidos += 1

        proximos = []
        if visitados == todos:
            proximos.append(('U', visitados))
        else:
            for i in range(n):
                if not esta_no_conjunto(visitados, i):
                    proximos.append((ginasios[i], colocar_no_conjunto(visitados, i)))

        for proximo, novos_visitados in proximos:
            novo_g = g + custos[(atual, proximo)]
            estado = (proximo, novos_visitados)

            if estado not in melhor_g or novo_g < melhor_g[estado]:
                melhor_g[estado] = novo_g
                anteriores[estado] = (atual, visitados)

                if proximo == 'U':
                    h = 0
                else:
                    h = calcular_heuristica(proximo, novos_visitados, chave, posicoes_chave, tabela, custos)

                heapq.heappush(fronteira, (novo_g + h, novo_g, proximo, novos_visitados))

    ordem = []
    estado = anteriores[('U', todos)]
    while estado is not None and estado[0] != '1':
        ordem.append(estado[0])
        estado = anteriores[estado]
    ordem.reverse()

    return ordem, melhor_g[('U', todos)], expandidos


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


