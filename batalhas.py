import random
import math
import copy
from mapa import POKEMONS, DIFICULDADE_GINASIOS

# Calcula o tempo gasto em um ginasio dividindo a dificuldade pelo poder total
def calcular_tempo_batalha(dificuldade, equipa_selecionada):
    if len(equipa_selecionada) == 0:
        return float('inf')
    
    poder_total = 0.0
    for pokemon in equipa_selecionada:
        poder_total += POKEMONS[pokemon]['poder']
        
    tempo = dificuldade / poder_total
    return tempo

# Calcula o custo total das batalhas e verifica se as regras de energia foram quebradas
def avaliar_solucao(solucao, ordem_ginasios):
    energia_atual = {}
    for p in POKEMONS:
        energia_atual[p] = POKEMONS[p]['energia']
        
    tempo_total = 0.0
    
    for ginasio in ordem_ginasios:
        equipe = solucao[ginasio]
        dificuldade = DIFICULDADE_GINASIOS[ginasio]
        
        tempo_batalha = calcular_tempo_batalha(dificuldade, equipe)
        tempo_total += tempo_batalha
        
        for pokemon in equipe:
            energia_atual[pokemon] -= 1
            # Se algum pokemon ficar com energia negativa, a solucao e invalida
            if energia_atual[pokemon] < 0:
                return float('inf'), energia_atual
                
    # Checa se sobrou pelo menos um pokemon com energia >= 1 no final do trajeto
    maior_energia = max(energia_atual.values())
    if maior_energia < 1:
        return float('inf'), energia_atual
        
    return tempo_total, energia_atual

# Modifica a equipe de um ginasio escolhido de forma aleatoria para gerar um vizinho
def gerar_vizinho(solucao_atual):
    novo_vizinho = copy.deepcopy(solucao_atual)
    
    lista_ginasios = list(novo_vizinho.keys())
    ginasio_aleatorio = random.choice(lista_ginasios)
    
    todos_pokemons = list(POKEMONS.keys())
    tamanho_equipe = random.randint(1, len(todos_pokemons))
    nova_equipe = random.sample(todos_pokemons, tamanho_equipe)
    
    novo_vizinho[ginasio_aleatorio] = nova_equipe
    
    return novo_vizinho

# Otimiza as equipes usando o algoritmo de Hill Climbing
def hill_climbing(ordem_ginasios, iteracoes=1000):
    # Gera uma solucao inicial aleatoria
    solucao_atual = {}
    for ginasio in ordem_ginasios:
        qtd_pokemons = random.randint(1, 3)
        solucao_atual[ginasio] = random.sample(list(POKEMONS.keys()), qtd_pokemons)
        
    custo_atual, _ = avaliar_solucao(solucao_atual, ordem_ginasios)
    
    for i in range(iteracoes):
        vizinho = gerar_vizinho(solucao_atual)
        custo_vizinho, _ = avaliar_solucao(vizinho, ordem_ginasios)
        
        # Aceita a mudanca apenas se o custo for menor
        if custo_vizinho < custo_atual:
            solucao_atual = vizinho
            custo_atual = custo_vizinho
            
    _, energia_final = avaliar_solucao(solucao_atual, ordem_ginasios)
    return solucao_atual, custo_atual, energia_final

# Otimiza as equipes usando o algoritmo de Simulated Annealing
def simulated_annealing(ordem_ginasios, temp_inicial=1000.0, taxa_arrefecimento=0.95, iteracoes=1000):
    solucao_atual = {}
    for ginasio in ordem_ginasios:
        qtd_pokemons = random.randint(1, 3)
        solucao_atual[ginasio] = random.sample(list(POKEMONS.keys()), qtd_pokemons)
        
    custo_atual, _ = avaliar_solucao(solucao_atual, ordem_ginasios)
    
    melhor_solucao = copy.deepcopy(solucao_atual)
    melhor_custo = custo_atual
    temperatura = temp_inicial
    
    for i in range(iteracoes):
        vizinho = gerar_vizinho(solucao_atual)
        custo_vizinho, _ = avaliar_solucao(vizinho, ordem_ginasios)
        
        delta_custo = custo_vizinho - custo_atual
        
        # Aceita se for melhor, ou se a probabilidade da temperatura permitir
        if delta_custo < 0:
            aceitar = True
        else:
            if temperatura > 0:
                probabilidade = math.exp(-delta_custo / temperatura)
                aceitar = random.random() < probabilidade
            else:
                aceitar = False
                
        if aceitar:
            solucao_atual = copy.deepcopy(vizinho)
            custo_atual = custo_vizinho
            
            if custo_atual < melhor_custo:
                melhor_solucao = copy.deepcopy(solucao_atual)
                melhor_custo = custo_atual
                
        temperatura = temperatura * taxa_arrefecimento
        
    _, energia_final = avaliar_solucao(melhor_solucao, ordem_ginasios)
    return melhor_solucao, melhor_custo, energia_final

# Operador de cruzamento (crossover) para o Algoritmo Genetico
def cruzar(pai1, pai2, ordem_ginasios):
    filho = {}
    ponto_corte = random.randint(1, len(ordem_ginasios) - 1)
    
    for i in range(len(ordem_ginasios)):
        ginasio = ordem_ginasios[i]
        if i < ponto_corte:
            filho[ginasio] = pai1[ginasio]
        else:
            filho[ginasio] = pai2[ginasio]
            
    return filho

# Operador de mutacao para o Algoritmo Genetico
def mutar(solucao, taxa_mutacao=0.1):
    chance = random.random()
    if chance < taxa_mutacao:
        return gerar_vizinho(solucao)
    else:
        return solucao

# Otimiza as equipes usando Algoritmo Genetico
def algoritmo_genetico(ordem_ginasios, tam_populacao=50, geracoes=100):
    # Cria a populacao inicial
    populacao = []
    for _ in range(tam_populacao):
        individuo = {}
        for ginasio in ordem_ginasios:
            qtd_pokemons = random.randint(1, 3)
            individuo[ginasio] = random.sample(list(POKEMONS.keys()), qtd_pokemons)
        populacao.append(individuo)
        
    avaliacoes = []
    
    for geracao in range(geracoes):
        # Avalia todo mundo da populacao
        avaliacoes = []
        for individuo in populacao:
            custo, _ = avaliar_solucao(individuo, ordem_ginasios)
            avaliacoes.append((individuo, custo))
            
        # Remove os invalidos e ordena do menor custo para o maior
        avaliacoes_validas = []
        for ind, custo in avaliacoes:
            if custo != float('inf'):
                avaliacoes_validas.append((ind, custo))
                
        avaliacoes = sorted(avaliacoes_validas, key=lambda x: x[1])
        
        # Se todo mundo for invalido, usa o hill climbing como seguranca
        if len(avaliacoes) == 0:
             return hill_climbing(ordem_ginasios)
             
        # Separa a elite (metade melhor)
        metade = tam_populacao // 2
        elite = []
        for i in range(min(metade, len(avaliacoes))):
            elite.append(avaliacoes[i][0])
            
        nova_populacao = copy.deepcopy(elite)
        
        # Completa o resto da populacao com filhos da elite
        while len(nova_populacao) < tam_populacao:
            pai1 = random.choice(elite)
            pai2 = random.choice(elite)
            
            filho = cruzar(pai1, pai2, ordem_ginasios)
            filho_mutado = mutar(filho)
            
            nova_populacao.append(filho_mutado)
            
        populacao = nova_populacao

    # Pega o melhor de todos no final
    melhor_individuo = avaliacoes[0][0]
    melhor_custo = avaliacoes[0][1]
    _, energia_final = avaliar_solucao(melhor_individuo, ordem_ginasios)
    
    return melhor_individuo, melhor_custo, energia_final