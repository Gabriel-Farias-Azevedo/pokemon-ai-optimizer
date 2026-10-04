import heapq
from mapa import obter_custo_movimento, DIFICULDADE_GINASIOS

# Calcula a distancia de Manhattan entre dois pontos na grade
def distancia_manhattan(ponto1, ponto2):
    return abs(ponto1[0] - ponto2[0]) + abs(ponto1[1] - ponto2[1])

# Pega as posicoes vizinhas validas (cima, baixo, esquerda, direita)[cite: 5]
def obter_vizinhos(mapa, x, y):
    vizinhos = []
    movimentos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    linhas = len(mapa)
    colunas = len(mapa[0])
    
    for mov_x, mov_y in movimentos:
        novo_x = x + mov_x
        novo_y = y + mov_y
        if 0 <= novo_x < linhas and 0 <= novo_y < colunas:
            vizinhos.append((novo_x, novo_y))
            
    return vizinhos

# Executa um A* simples para achar o menor caminho e custo entre dois pontos especificos do mapa
def menor_caminho_entre_pontos(mapa, origem, destino):
    fronteira = []
    heapq.heappush(fronteira, (0, origem, [origem]))
    custos_minimos = {origem: 0}
    
    while len(fronteira) > 0:
        _, atual, caminho = heapq.heappop(fronteira)
        
        if atual == destino:
            return caminho, custos_minimos[atual]
            
        for vizinho in obter_vizinhos(mapa, atual[0], atual[1]):
            custo_passo = obter_custo_movimento(mapa[vizinho[0]][vizinho[1]])
            novo_custo = custos_minimos[atual] + custo_passo
            
            if vizinho not in custos_minimos or novo_custo < custos_minimos[vizinho]:
            # Se encontrou um caminho melhor para este vizinho, atualiza
                custos_minimos[vizinho] = novo_custo
                prioridade = novo_custo + distancia_manhattan(vizinho, destino)
                novo_caminho = list(caminho)
                novo_caminho.append(vizinho)
                heapq.heappush(fronteira, (prioridade, vizinho, novo_caminho))
                
    return None, float('inf')

# Cria uma tabela pre-calculada de custos entre todos os ginasios, origem e destino
def pre_calcular_distancias(mapa, inicio, destino, coords_ginasios):
    todos_pontos = { '1': inicio, 'U': destino }
    for ginasio, coords in coords_ginasios.items():
        todos_pontos[ginasio] = coords
        
    tabela_custos = {}
    tabela_caminhos = {}
    
    chaves = list(todos_pontos.keys())
    for i in range(len(chaves)):
        for j in range(len(chaves)):
            if i != j:
                p1_id = chaves[i]
                p2_id = chaves[j]
                caminho, custo = menor_caminho_entre_pontos(mapa, todos_pontos[p1_id], todos_pontos[p2_id])
                tabela_custos[(p1_id, p2_id)] = custo
                tabela_caminhos[(p1_id, p2_id)] = caminho
                
    return tabela_custos, tabela_caminhos, todos_pontos

class EstadoGrafo:
    # Guarda o estado atual da busca baseada nos ginasios ja visitados[cite: 2]
    def __init__(self, id_atual, ginasios_visitados, custo_g, coords_ginasios, destino_id, tabela_custos, todos_pontos):
        self.id_atual = id_atual
        self.ginasios_visitados = frozenset(ginasios_visitados)
        self.custo_g = custo_g
        self.coords_ginasios = coords_ginasios
        self.destino_id = destino_id
        self.tabela_custos = tabela_custos
        self.todos_pontos = todos_pontos
        
        h = self.heuristica()
        self.custo_f = self.custo_g + h

    # Calcula a heuristica admissivel usando o menor custo ate o proximo ginasio restante
    def heuristica(self):
        ginasios_faltantes = []
        for ginasio_id in self.coords_ginasios:
            if ginasio_id not in self.ginasios_visitados:
                ginasios_faltantes.append(ginasio_id)
                
        # Se ja visitou todos os 24, a heuristica e o custo ate o destino final U[cite: 2, 7]
        if len(ginasios_faltantes) == 0:
            if (self.id_atual, self.destino_id) in self.tabela_custos:
                return self.tabela_custos[(self.id_atual, self.destino_id)]
            return 0
            
        # Pega a menor distancia pre-calculada ate qualquer ginasio que falta visitar
        menor = float('inf')
        for g_id in ginasios_faltantes:
            if (self.id_atual, g_id) in self.tabela_custos:
                custo = self.tabela_custos[(self.id_atual, g_id)]
                if custo < menor:
                    menor = custo
                    
        return menor if menor != float('inf') else 0

    def __lt__(self, outro):
        return self.custo_f < outro.custo_f

# Varre a matriz pra achar onde esta cada ginasio
def mapear_coordenadas_ginasios(mapa):
    coords = {}
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            celula = mapa[i][j]
            if celula in DIFICULDADE_GINASIOS:
                coords[celula] = (i, j)
    return coords

# Algoritmo A* otimizado usando o grafo reduzido de pontos de interesse[cite: 1, 2]
def busca_a_estrela(mapa, inicio, destino):
    coords_ginasios = mapear_coordenadas_ginasios(mapa)
    total_ginasios = set(coords_ginasios.keys())
    
    # Pre-calcula os caminhos exatos entre todos os pontos importantes de Kanto
    tabela_custos, tabela_caminhos, todos_pontos = pre_calcular_distancias(mapa, inicio, destino, coords_ginasios)
    
    # Estado inicial no noh '1' (origem)[cite: 2, 7]
    estado_inicial = EstadoGrafo('1', set(), 0, coords_ginasios, 'U', tabela_custos, todos_pontos)
    fronteira = []
    
    # Guarda o custo_f, o estado e a lista de IDs dos locais visitados no grafo
    heapq.heappush(fronteira, (estado_inicial.custo_f, estado_inicial, ['1']))
    
    visitados = set()

    while len(fronteira) > 0:
        _, estado_atual, sequencia_ids = heapq.heappop(fronteira)
        
        estado_hash = (estado_atual.id_atual, estado_atual.ginasios_visitados)
        if estado_hash in visitados:
            continue
        visitados.add(estado_hash)
        
        # Se chegou ao destino U e passou pelos 24 ginasios[cite: 2]
        if estado_atual.id_atual == 'U' and set(estado_atual.ginasios_visitados) == total_ginasios:
            # Reconstrói o caminho completo de coordenadas (pixels/celulas do mapa)
            caminho_completo = []
            for k in range(len(sequencia_ids) - 1):
                p_origem = sequencia_ids[k]
                p_destino = sequencia_ids[k+1]
                trecho = tabela_caminhos[(p_origem, p_destino)]
                if k > 0:
                    trecho = trecho[1:] # Evita duplicar o noh de conexao
                caminho_completo.extend(trecho)
            return caminho_completo, estado_atual.custo_g

        # Expande para todos os destinos possiveis (os ginasios restantes ou o destino final)
        proximos_possiveis = list(coords_ginasios.keys()) + ['U']
        
        for proximo_id in proximos_possiveis:
            if proximo_id == 'U' and set(estado_atual.ginasios_visitados) != total_ginasios:
                continue # Nao pode ir pro destino final antes de visitar todos os ginasios
                
            novos_ginasios = set(estado_atual.ginasios_visitados)
            if proximo_id in coords_ginasios:
                novos_ginasios.add(proximo_id)
                
            custo_trecho = tabela_custos.get((estado_atual.id_atual, proximo_id), float('inf'))
            if custo_trecho == float('inf'):
                continue
                
            novo_custo_g = estado_atual.custo_g + custo_trecho
            novo_estado = EstadoGrafo(proximo_id, novos_ginasios, novo_custo_g, coords_ginasios, 'U', tabela_custos, todos_pontos)
            
            novo_hash = (proximo_id, novo_estado.ginasios_visitados)
            if novo_hash not in visitados:
                novo_sequencia = list(sequencia_ids)
                novo_sequencia.append(proximo_id)
                heapq.heappush(fronteira, (novo_estado.custo_f, novo_estado, novo_sequencia))

    return None, float('inf')