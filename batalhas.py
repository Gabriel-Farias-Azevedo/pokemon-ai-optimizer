import copy
import math
import random

from mapa import DIFICULDADE_GINASIOS, POKEMONS

def calcular_tempo_batalha(dificuldade, equipe):
    if not equipe:
        return float('inf')

    poder = sum(POKEMONS[pokemon]['poder'] for pokemon in equipe)
    return dificuldade / poder


def avaliar_solucao(individuo, tabela_custos):
    ordem, equipes = individuo
    energia = {pokemon: dados['energia'] for pokemon, dados in POKEMONS.items()}
    tempo_rota = 0
    tempo_batalhas = 0

    pontos = ['1'] + ordem + ['U']

    for i in range(len(pontos) - 1):
        origem, destino = pontos[i], pontos[i + 1]
        tempo_rota += tabela_custos.get((origem, destino), float('inf'))

    for ginasio in ordem:
        equipe = equipes[ginasio]
        tempo_batalhas += calcular_tempo_batalha(DIFICULDADE_GINASIOS[ginasio], equipe)

        for pokemon in equipe:
            energia[pokemon] -= 1
            if energia[pokemon] < 0:
                return float('inf'), energia

    if max(energia.values()) < 1:
        return float('inf'), energia

    return tempo_rota + tempo_batalhas, energia


def gerar_vizinho(individuo):
    ordem, equipes = copy.deepcopy(individuo)

    if random.random() < 0.5 and len(ordem) > 1:
        i, j = random.sample(range(len(ordem)), 2)
        ordem[i], ordem[j] = ordem[j], ordem[i]
    else:
        ginasio = random.choice(ordem)
        quantidade = random.randint(1, min(2, len(POKEMONS)))
        equipes[ginasio] = random.sample(list(POKEMONS), quantidade)

    return ordem, equipes


def gerar_individuo_aleatorio(ginasios):
    ordem = ginasios.copy()
    random.shuffle(ordem)

    equipes = {
        ginasio: random.sample(list(POKEMONS), 1)
        for ginasio in ordem
    }

    return ordem, equipes


def hill_climbing(ginasios, tabela_custos, iteracoes=3000):
    atual = gerar_individuo_aleatorio(ginasios)
    custo_atual, _ = avaliar_solucao(atual, tabela_custos)

    for _ in range(iteracoes):
        vizinho = gerar_vizinho(atual)
        custo_vizinho, _ = avaliar_solucao(vizinho, tabela_custos)

        if custo_vizinho < custo_atual:
            atual = vizinho
            custo_atual = custo_vizinho

    _, energia = avaliar_solucao(atual, tabela_custos)
    return atual, custo_atual, energia


def simulated_annealing(ginasios, tabela_custos, temp_inicial=2000.0, taxa_arrefecimento=0.98, iteracoes=3000):
    atual = gerar_individuo_aleatorio(ginasios)
    custo_atual, _ = avaliar_solucao(atual, tabela_custos)

    melhor = copy.deepcopy(atual)
    melhor_custo = custo_atual
    temperatura = temp_inicial

    for _ in range(iteracoes):
        vizinho = gerar_vizinho(atual)
        custo_vizinho, _ = avaliar_solucao(vizinho, tabela_custos)
        diferenca = custo_vizinho - custo_atual

        aceita = diferenca < 0
        if not aceita and temperatura > 0:
            aceita = random.random() < math.exp(-diferenca / temperatura)

        if aceita:
            atual = copy.deepcopy(vizinho)
            custo_atual = custo_vizinho

            if custo_atual < melhor_custo:
                melhor = copy.deepcopy(atual)
                melhor_custo = custo_atual

        temperatura *= taxa_arrefecimento

    _, energia = avaliar_solucao(melhor, tabela_custos)
    return melhor, melhor_custo, energia


def cruzar(pai1, pai2):
    ordem1, equipes1 = pai1
    ordem2, equipes2 = pai2
    tamanho = len(ordem1)

    inicio, fim = sorted(random.sample(range(tamanho), 2))
    nova_ordem = [None] * tamanho
    nova_ordem[inicio:fim] = ordem1[inicio:fim]

    posicao = 0
    for i in range(tamanho):
        if nova_ordem[i] is None:
            while ordem2[posicao] in nova_ordem:
                posicao += 1
            nova_ordem[i] = ordem2[posicao]

    novas_equipes = {}
    for ginasio in nova_ordem:
        if random.random() < 0.5:
            novas_equipes[ginasio] = equipes1[ginasio]
        else:
            novas_equipes[ginasio] = equipes2[ginasio]

    return nova_ordem, novas_equipes


def mutar(solucao, taxa=0.2):
    if random.random() < taxa:
        return gerar_vizinho(solucao)
    return solucao


def algoritmo_genetico(ginasios, tabela_custos, tam_populacao=100, geracoes=200):
    populacao = [
        gerar_individuo_aleatorio(ginasios)
        for _ in range(tam_populacao)
    ]

    for _ in range(geracoes):
        avaliados = []

        for individuo in populacao:
            custo, _ = avaliar_solucao(individuo, tabela_custos)
            if custo != float('inf'):
                avaliados.append((individuo, custo))

        if not avaliados:
            return hill_climbing(ginasios, tabela_custos)

        avaliados.sort(key=lambda item: item[1])
        elite = [individuo for individuo, _ in avaliados[:tam_populacao // 2]]
        nova_populacao = copy.deepcopy(elite)

        while len(nova_populacao) < tam_populacao:
            pai1 = random.choice(elite)
            pai2 = random.choice(elite)
            filho = mutar(cruzar(pai1, pai2))
            nova_populacao.append(filho)

        populacao = nova_populacao

    avaliados = [
        (individuo, avaliar_solucao(individuo, tabela_custos)[0])
        for individuo in populacao
    ]
    avaliados.sort(key=lambda item: item[1])

    melhor, custo = avaliados[0]
    _, energia = avaliar_solucao(melhor, tabela_custos)

    return melhor, custo, energia


