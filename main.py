import random
import statistics

from batalhas import algoritmo_genetico, simulated_annealing, hill_climbing
from batalhas import calcular_energia, calcular_tempo_batalha, solucao_valida
from mapa import DIFICULDADE_GINASIOS, carregar_mapa
from rota import a_estrela_ginasios, gerar_matriz_distancias, reconstruir_rota_completa


def encontrar_inicio_e_destino(mapa):
    inicio = None
    destino = None

    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if mapa[i][j] == '1':
                inicio = (i, j)
            elif mapa[i][j] == 'U':
                destino = (i, j)

    return inicio, destino


def executar_experimentos(algoritmo, ginasios, execucoes=30):
    resultados = []
    melhor_solucao = None
    melhor_custo = float('inf')

    for _ in range(execucoes):
        solucao, custo = algoritmo(ginasios)

        if not solucao_valida(solucao):
            continue

        resultados.append(custo)

        if custo < melhor_custo:
            melhor_custo = custo
            melhor_solucao = solucao

    if len(resultados) == 0:
        return None, float('inf')

    media = statistics.mean(resultados)
    if len(resultados) > 1:
        desvio = statistics.stdev(resultados)
    else:
        desvio = 0.0

    print("Execuções:", execucoes, "| Válidas:", len(resultados), "| Melhor:", round(melhor_custo, 3),
          "| Média:", round(media, 3), "| Desvio:", round(desvio, 3))

    return melhor_solucao, melhor_custo


def mostrar_percurso(ordem, custos, equipes):
    pontos = ['1'] + ordem + ['U']
    custo_rota = 0
    custo_batalhas = 0

    print("\nPercurso do agente:")
    for i in range(1, len(pontos)):
        anterior = pontos[i - 1]
        ponto = pontos[i]
        custo_rota += custos[(anterior, ponto)]

        if ponto == 'U':
            print("  Chegou em U | rota:", custo_rota, "| batalhas:", round(custo_batalhas, 3))
        else:
            custo_batalhas += calcular_tempo_batalha(DIFICULDADE_GINASIOS[ponto], equipes[ponto])
            print("  Ginásio", ponto, "| rota:", custo_rota, "| batalhas:", round(custo_batalhas, 3),
                  "| equipe:", ", ".join(equipes[ponto]))

    return custo_rota, custo_batalhas


def main():
    random.seed(42)

    with open("mapa.txt", "r", encoding="utf-8") as arquivo:
        mapa = carregar_mapa(arquivo.read())

    inicio, destino = encontrar_inicio_e_destino(mapa)

    if inicio is None or destino is None:
        print("Erro: origem (1) ou destino (U) não encontrados no mapa.")
        return

    custos, caminhos, ginasios = gerar_matriz_distancias(mapa, inicio, destino)

    print("\nBuscando a melhor ordem dos ginásios com A* : ")
    ordem, custo_rota, expandidos = a_estrela_ginasios(ginasios, custos)
    print("Custo da rota:", custo_rota, "| Estados expandidos pelo A*:", expandidos)

    rota_completa = reconstruir_rota_completa(ordem, caminhos)

    testes = 30

    print("\nHill Climbing : ")
    solucao_hc, custo_hc = executar_experimentos(hill_climbing, ginasios, testes)

    print("\nSimulated Annealing:")
    solucao_sa, custo_sa = executar_experimentos(simulated_annealing, ginasios, testes)

    print("\nAlgoritmo Genético: ")
    solucao_ag, custo_ag = executar_experimentos(algoritmo_genetico, ginasios, testes)

    nome = "Hill Climbing"
    equipes = solucao_hc
    custo_batalhas = custo_hc

    if custo_sa < custo_batalhas:
        nome = "Simulated Annealing"
        equipes = solucao_sa
        custo_batalhas = custo_sa

    if custo_ag < custo_batalhas:
        nome = "Algoritmo Genético"
        equipes = solucao_ag
        custo_batalhas = custo_ag

    custo_rota, custo_batalhas = mostrar_percurso(ordem, custos, equipes)

    print("\n RESULTADO: ")
    print("Melhor algoritmo nas batalhas:", nome)
    print("Ordem de visita aos ginásios:", " -> ".join(ordem))
    print("Pokemon usados em cada batalha:")
    for ginasio in ordem:
        print(" " + ginasio + ":", ", ".join(equipes[ginasio]))
    print("Energia final de cada Pokemon:", calcular_energia(equipes))
    print("Estados expandidos pelo A*:", expandidos)
    print("Passos no mapa:", len(rota_completa) - 1)
    print("Custo da rota (C_rota):", custo_rota, "minutos")
    print("Custo das batalhas (C_batalhas):", round(custo_batalhas, 3), "minutos")
    print("Custo total (C_total):", round(custo_rota + custo_batalhas, 3), "minutos")


if __name__ == "__main__":
    main()
