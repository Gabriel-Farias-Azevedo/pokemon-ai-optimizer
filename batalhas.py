import math
import random

from mapa import DIFICULDADE_GINASIOS, POKEMONS

PENALIDADE = 1000


def calcular_tempo_batalha(dificuldade, equipe):
    poder_total = 0
    for pokemon in equipe:
        poder_total += POKEMONS[pokemon]['poder']

    return dificuldade / poder_total


def calcular_energia(equipes):
    energia = {}
    for pokemon in POKEMONS:
        energia[pokemon] = POKEMONS[pokemon]['energia']

    for ginasio in equipes:
        for pokemon in equipes[ginasio]:
            energia[pokemon] -= 1

    return energia


def avaliar_solucao(equipes):
    tempo_batalhas = 0
    for ginasio in equipes:
        tempo_batalhas += calcular_tempo_batalha(DIFICULDADE_GINASIOS[ginasio], equipes[ginasio])

    energia = calcular_energia(equipes)

    violacoes = 0
    for pokemon in energia:
        if energia[pokemon] < 0:
            violacoes += -energia[pokemon]

    if max(energia.values()) < 1:
        violacoes += 1

    return tempo_batalhas + PENALIDADE * violacoes


def solucao_valida(equipes):
    energia = calcular_energia(equipes)

    ninguem_negativo = min(energia.values()) >= 0
    alguem_acordado = max(energia.values()) >= 1

    return ninguem_negativo and alguem_acordado


def gerar_solucao_inicial(ginasios):
    ordem = ginasios.copy()
    random.shuffle(ordem)
    pokemons = list(POKEMONS)
    random.shuffle(pokemons)

    solucao = {}
    vez = 0
    for ginasio in ordem:
        solucao[ginasio] = [pokemons[vez]]
        vez += 1
        if vez == len(pokemons):
            vez = 0

    return solucao


def copiar(equipes):
    copia = {}
    for ginasio in equipes:
        copia[ginasio] = list(equipes[ginasio])

    return copia


def gerar_vizinho(equipes):
    vizinho = copiar(equipes)

    ginasio = random.choice(list(vizinho))
    equipe = vizinho[ginasio]

    fora = []
    for pokemon in POKEMONS:
        if pokemon not in equipe:
            fora.append(pokemon)

    outro_ginasio = random.choice(list(vizinho))
    outra_equipe = vizinho[outro_ginasio]

    acao = random.choice(['adicionar', 'remover', 'trocar', 'trocar_entre', 'mover'])

    if acao == 'adicionar':
        if len(fora) > 0:
            equipe.append(random.choice(fora))

    elif acao == 'remover':
        if len(equipe) > 1:
            equipe.remove(random.choice(equipe))
        else:
            equipe.remove(random.choice(equipe))
            equipe.append(random.choice(fora))

    elif acao == 'trocar':
        if len(fora) > 0:
            equipe.remove(random.choice(equipe))
            equipe.append(random.choice(fora))

    elif acao == 'trocar_entre':
        p1 = random.choice(equipe)
        p2 = random.choice(outra_equipe)
        if p2 not in equipe and p1 not in outra_equipe:
            posicao1 = equipe.index(p1)
            posicao2 = outra_equipe.index(p2)
            equipe[posicao1] = p2
            outra_equipe[posicao2] = p1

    elif acao == 'mover':
        p = random.choice(equipe)
        if len(equipe) > 1 and p not in outra_equipe:
            equipe.remove(p)
            outra_equipe.append(p)

    return vizinho


def hill_climbing(ginasios, iteracoes=20000):
    atual = gerar_solucao_inicial(ginasios)
    custo_atual = avaliar_solucao(atual)

    for _ in range(iteracoes):
        vizinho = gerar_vizinho(atual)
        custo_vizinho = avaliar_solucao(vizinho)

        if custo_vizinho <= custo_atual:
            atual = vizinho
            custo_atual = custo_vizinho

    return atual, custo_atual


def simulated_annealing(ginasios, temp_inicial=30.0, taxa_arrefecimento=0.9996, iteracoes=20000):
    atual = gerar_solucao_inicial(ginasios)
    custo_atual = avaliar_solucao(atual)

    melhor = copiar(atual)
    melhor_custo = custo_atual
    temperatura = temp_inicial

    for _ in range(iteracoes):
        vizinho = gerar_vizinho(atual)
        custo_vizinho = avaliar_solucao(vizinho)
        diferenca = custo_vizinho - custo_atual

        if diferenca <= 0:
            aceita = True
        else:
            chance = math.exp(-diferenca / temperatura)
            aceita = random.random() < chance

        if aceita:
            atual = vizinho
            custo_atual = custo_vizinho

            if custo_atual < melhor_custo:
                melhor = copiar(atual)
                melhor_custo = custo_atual

        temperatura = temperatura * taxa_arrefecimento

    return melhor, melhor_custo


def cruzar(pai1, pai2):
    filho = {}
    for ginasio in pai1:
        if random.random() < 0.5:
            filho[ginasio] = list(pai1[ginasio])
        else:
            filho[ginasio] = list(pai2[ginasio])

    return filho


def mutar(solucao, taxa=0.3):
    if random.random() < taxa:
        return gerar_vizinho(solucao)

    return solucao


def torneio(avaliados, tamanho=3):
    competidores = random.sample(avaliados, tamanho)

    vencedor, custo_vencedor = competidores[0]
    for solucao, custo in competidores:
        if custo < custo_vencedor:
            vencedor = solucao
            custo_vencedor = custo

    return vencedor


def pegar_custo(item):
    return item[1]


def algoritmo_genetico(ginasios, tam_populacao=60, geracoes=200):
    populacao = []
    for _ in range(tam_populacao):
        populacao.append(gerar_solucao_inicial(ginasios))

    for _ in range(geracoes):
        avaliados = []
        for individuo in populacao:
            avaliados.append((individuo, avaliar_solucao(individuo)))
        avaliados.sort(key=pegar_custo)

        nova_populacao = [avaliados[0][0], avaliados[1][0]]

        while len(nova_populacao) < tam_populacao:
            pai1 = torneio(avaliados)
            pai2 = torneio(avaliados)
            filho = cruzar(pai1, pai2)
            filho = mutar(filho)
            nova_populacao.append(filho)

        populacao = nova_populacao

    melhor = populacao[0]
    melhor_custo = avaliar_solucao(melhor)
    for individuo in populacao:
        custo = avaliar_solucao(individuo)
        if custo < melhor_custo:
            melhor = individuo
            melhor_custo = custo

    return melhor, melhor_custo

