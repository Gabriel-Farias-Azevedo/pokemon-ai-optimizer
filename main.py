import statistics

from batalhas import algoritmo_genetico, hill_climbing, simulated_annealing
from mapa import carregar_mapa
from rota import gerar_matriz_distancias, reconstruir_rota_completa


def encontrar_inicio_e_destino(mapa):
    inicio = None
    destino = None

    for i, linha in enumerate(mapa):
        for j, celula in enumerate(linha):
            if celula == '1':
                inicio = (i, j)
            elif celula == 'U':
                destino = (i, j)

    return inicio, destino


def executar_experimentos(funcao, ginasios, custos, execucoes=30, **parametros):
    resultados = []
    melhor_solucao = None
    melhor_custo = float('inf')
    melhor_energia = None

    for _ in range(execucoes):
        solucao, custo, energia = funcao(ginasios, custos, **parametros)

        if custo == float('inf'):
            continue

        resultados.append(custo)

        if custo < melhor_custo:
            melhor_custo = custo
            melhor_solucao = solucao
            melhor_energia = energia

    if not resultados:
        return None, float('inf'), 0, 0, None

    media = statistics.mean(resultados)
    desvio = statistics.stdev(resultados) if len(resultados) > 1 else 0.0

    return melhor_solucao, melhor_custo, media, desvio, melhor_energia


def main():
    with open("mapa.txt", "r") as arquivo:
        mapa = carregar_mapa(arquivo.read())

    inicio, destino = encontrar_inicio_e_destino(mapa)

    if inicio is None or destino is None:
        print("Erro: origem (1) ou destino (U) não encontrados no mapa.")
        return

    print("Pré-calculando distâncias com Dijkstra...")
    custos, caminhos, ginasios = gerar_matriz_distancias(mapa, inicio, destino)

    print("\nOtimizando rota e batalhas...")
    testes = 100

    print("\nExecutando Hill Climbing...")
    solucao_hc, custo_hc, media_hc, desvio_hc, energia_hc = executar_experimentos(
        hill_climbing, ginasios, custos, testes, iteracoes=1000
    )
    print(f"Testes: {testes} | Média: {media_hc:.2f} | Desvio: {desvio_hc:.2f} | "
          f"Melhor Custo: {custo_hc:.2f}")

    print("\nExecutando Simulated Annealing...")
    solucao_sa, custo_sa, media_sa, desvio_sa, energia_sa = executar_experimentos(
        simulated_annealing, ginasios, custos, testes, iteracoes=1000
    )
    print(f"Testes: {testes} | Média: {media_sa:.2f} | Desvio: {desvio_sa:.2f} | "
          f"Melhor Custo: {custo_sa:.2f}")

    print("\nExecutando Algoritmo Genético...")
    solucao_ag, custo_ag, media_ag, desvio_ag, energia_ag = executar_experimentos(
        algoritmo_genetico, ginasios, custos, testes, geracoes=50
    )
    print(f"Testes: {testes} | Média: {media_ag:.2f} | Desvio: {desvio_ag:.2f} | "
          f"Melhor Custo: {custo_ag:.2f}")

    resultados = [
        ("Hill Climbing", solucao_hc, custo_hc, energia_hc),
        ("Simulated Annealing", solucao_sa, custo_sa, energia_sa),
        ("Algoritmo Genético", solucao_ag, custo_ag, energia_ag)
    ]

    melhor = resultados[0]

    for resultado in resultados[1:]:
        if resultado[2] < melhor[2]:
            melhor = resultado

    nome, solucao, custo, energia = melhor
    ordem, equipes = solucao

    reconstruir_rota_completa(ordem, caminhos)

    print(f"Melhor Algoritmo Unificado: {nome}")
    print(f"Ordem de visita aos ginásios: {ordem}")
    print(f"Pokémon usados em cada batalha: {equipes}")
    print(f"Energia final de cada Pokémon: {energia}")
    print(f"Custo Total (C_total): {custo:.2f} minutos")
    
if __name__ == "__main__":
    main()