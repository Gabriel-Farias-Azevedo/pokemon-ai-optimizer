import heapq
from functools import lru_cache
from mapa import obter_custo_movimento, DIFICULDADE_GINASIOS

def obter_vizinhos(mapa, x, y):
    vizinhos = []
    movimentos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    linhas, colunas = len(mapa), len(mapa[0])

    for mov_x, mov_y in movimentos:
        novo_x, novo_y = x + mov_x, y + mov_y
        if 0 <= novo_x < linhas and 0 <= novo_y < colunas:
            vizinhos.append((novo_x, novo_y))
    return vizinhos

def dijkstra_todos_destinos(mapa, origem, destinos_coords):
    """
    Otimização: Encontra o menor caminho da origem para TODOS os outros pontos de 
    interesse em uma única varredura, ao invés de rodar uma busca por par.
    """
    fronteira = [(0, origem)]
    custos_minimos = {origem: 0}
    veio_de = {origem: None}
    
    pontos_restantes = set(destinos_coords.values())
    pontos_restantes.discard(origem)
    
    caminhos_encontrados = {}
    custos_encontrados = {}

    while fronteira and pontos_restantes:
        custo_atual, atual = heapq.heappop(fronteira)

        if atual in pontos_restantes:
            pontos_restantes.remove(atual)
            
        for vizinho in obter_vizinhos(mapa, atual[0], atual[1]):
            custo_passo = obter_custo_movimento(mapa[vizinho[0]][vizinho[1]])
            novo_custo = custos_minimos[atual] + custo_passo

            if vizinho not in custos_minimos or novo_custo < custos_minimos[vizinho]:
                custos_minimos[vizinho] = novo_custo
                veio_de[vizinho] = atual
                heapq.heappush(fronteira, (novo_custo, vizinho))

    # Reconstrói os caminhos apenas para os pontos de interesse
    for dest_id, dest_coord in destinos_coords.items():
        if dest_coord == origem or dest_coord not in custos_minimos:
            continue
            
        caminho = []
        nodo = dest_coord
        while nodo is not None:
            caminho.append(nodo)
            nodo = veio_de.get(nodo)
        caminho.reverse()
        
        caminhos_encontrados[dest_id] = caminho
        custos_encontrados[dest_id] = custos_minimos[dest_coord]

    return custos_encontrados, caminhos_encontrados

def pre_calcular_distancias(mapa, inicio, destino, coords_ginasios):
    todos_pontos = {'1': inicio, 'U': destino, **coords_ginasios}
    tabela_custos = {}
    tabela_caminhos = {}

    print(f"Pre-calculando matriz de distâncias para {len(todos_pontos)} pontos...")

    # Executa Dijkstra uma vez por ponto de origem
    for origem_id, origem_coord in todos_pontos.items():
        custos, caminhos = dijkstra_todos_destinos(mapa, origem_coord, todos_pontos)
        
        for destino_id, custo in custos.items():
            tabela_custos[(origem_id, destino_id)] = custo
            tabela_caminhos[(origem_id, destino_id)] = caminhos[destino_id]

    print("Pre-calculo concluído com sucesso!")
    return tabela_custos, tabela_caminhos, todos_pontos

@lru_cache(maxsize=None)
def calcular_mst_otimizado(faltantes_frozenset, tabela_custos_tuple):
    """
    Cálculo da Árvore Geradora Mínima com cache para evitar recálculos no A*.
    Tabela de custos convertida para tupla para ser 'hashable'.
    """
    if len(faltantes_frozenset) <= 1:
        return 0

    tabela_custos = dict(tabela_custos_tuple)
    ginasios = list(faltantes_frozenset)
    conectados = {ginasios[0]}
    custo_total = 0

    while len(conectados) < len(ginasios):
        menor_custo = float('inf')
        proximo = None

        for origem in conectados:
            for destino in ginasios:
                if destino in conectados:
                    continue
                custo = tabela_custos.get((origem, destino), float('inf'))
                if custo < menor_custo:
                    menor_custo = custo
                    proximo = destino

        if proximo is None: return float('inf')
        conectados.add(proximo)
        custo_total += menor_custo

    return custo_total

class EstadoGrafo:
    def __init__(self, id_atual, ginasios_visitados, custo_g, destinos_possiveis, destino_id, tabela_custos):
        self.id_atual = id_atual
        self.ginasios_visitados = ginasios_visitados
        self.custo_g = custo_g
        self.destinos_possiveis = destinos_possiveis
        self.destino_id = destino_id
        self.tabela_custos = tabela_custos
        self.custo_f = custo_g + self.heuristica()

    def heuristica(self):
        faltantes = frozenset(self.destinos_possiveis) - self.ginasios_visitados
        if not faltantes:
            return self.tabela_custos.get((self.id_atual, self.destino_id), float('inf'))

        menor_saida = min(self.tabela_custos.get((self.id_atual, g), float('inf')) for g in faltantes)
        menor_destino = min(self.tabela_custos.get((g, self.destino_id), float('inf')) for g in faltantes)
        
        # Converte dicionário para tupla para permitir uso do lru_cache
        tupla_custos = tuple(self.tabela_custos.items())
        mst = calcular_mst_otimizado(faltantes, tupla_custos)

        return menor_saida + mst + menor_destino

    def __lt__(self, outro):
        return self.custo_f < outro.custo_f

def reconstruir_caminho_grafo(estado_hash, veio_de, tabela_caminhos):
    sequencia = []
    while estado_hash is not None:
        sequencia.append(estado_hash[0])
        estado_hash = veio_de.get(estado_hash)
    sequencia.reverse()

    caminho_completo = []
    for i in range(len(sequencia) - 1):
        trecho = tabela_caminhos[(sequencia[i], sequencia[i + 1])]
        caminho_completo.extend(trecho if i == 0 else trecho[1:])
    return caminho_completo

def mapear_coordenadas_ginasios(mapa):
    coords = {}
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            celula = mapa[i][j]
            if celula in DIFICULDADE_GINASIOS:
                coords[celula] = (i, j)
    return coords

def busca_a_estrela(mapa, inicio, destino):
    # (Funções de mapeamento de coordenadas omitidas por brevidade - mantenha a sua mapear_coordenadas_ginasios)
    coords_ginasios = mapear_coordenadas_ginasios(mapa)
    total_ginasios = frozenset(coords_ginasios.keys())

    tabela_custos, tabela_caminhos, _ = pre_calcular_distancias(mapa, inicio, destino, coords_ginasios)

    print("Executando A* principal no grafo reduzido...")
    estado_inicial = EstadoGrafo('1', frozenset(), 0, total_ginasios, 'U', tabela_custos)
    
    fronteira = []
    contador = 0
    estado_inicial_hash = ('1', frozenset())
    veio_de = {estado_inicial_hash: None}
    melhores_custos = {estado_inicial_hash: 0}

    heapq.heappush(fronteira, (estado_inicial.custo_f, contador, estado_inicial))

    while fronteira:
        _, _, estado_atual = heapq.heappop(fronteira)
        estado_hash = (estado_atual.id_atual, estado_atual.ginasios_visitados)

        # Critério de parada: Chegamos no destino com todos os ginásios
        if estado_atual.id_atual == 'U' and estado_atual.ginasios_visitados == total_ginasios:
            caminho = reconstruir_caminho_grafo(estado_hash, veio_de, tabela_caminhos)
            return caminho, estado_atual.custo_g

        faltantes = total_ginasios - estado_atual.ginasios_visitados
        proximos = ['U'] if not faltantes else faltantes

        for proximo_id in proximos:
            custo_trecho = tabela_custos.get((estado_atual.id_atual, proximo_id), float('inf'))
            if custo_trecho == float('inf'): continue

            novos_ginasios = estado_atual.ginasios_visitados | ({proximo_id} if proximo_id in total_ginasios else set())
            novo_custo = estado_atual.custo_g + custo_trecho
            novo_hash = (proximo_id, novos_ginasios)

            # Evita estados repetidos ineficientes
            if novo_custo >= melhores_custos.get(novo_hash, float('inf')):
                continue

            melhores_custos[novo_hash] = novo_custo
            veio_de[novo_hash] = estado_hash

            novo_estado = EstadoGrafo(
                proximo_id, novos_ginasios, novo_custo, 
                total_ginasios, 'U', tabela_custos
            )

            contador += 1
            heapq.heappush(fronteira, (novo_estado.custo_f, contador, novo_estado))

    return None, float('inf')