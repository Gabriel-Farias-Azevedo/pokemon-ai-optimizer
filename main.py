import statistics
from mapa import carregar_mapa, DIFICULDADE_GINASIOS
from rota import busca_a_estrela
from batalhas import hill_climbing, simulated_annealing, algoritmo_genetico

# Acha a posicao exata da origem '1' e do destino 'U' varrendo a matriz do mapa
def encontrar_inicio_e_destino(mapa):
    inicio = None
    destino = None
    
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            celula = mapa[i][j]
            if celula == '1':
                inicio = (i, j)
            elif celula == 'U':
                destino = (i, j)
                
    return inicio, destino

# Roda a busca local varias vezes para tirar estatisticas de media e desvio padrao
def executar_experimentos(nome_algoritmo, func_busca, ordem_ginasios, num_execucoes=30):
    resultados = []
    melhor_solucao = None
    menor_custo = float('inf')
    melhor_energia = None

    for i in range(num_execucoes):
        solucao, custo, energia_final = func_busca(ordem_ginasios)
        
        if custo != float('inf'):
            resultados.append(custo)
            if custo < menor_custo:
                menor_custo = custo
                melhor_solucao = solucao
                melhor_energia = energia_final

    if len(resultados) == 0:
        return None, float('inf'), 0, 0, None

    media = statistics.mean(resultados)
    
    if len(resultados) > 1:
        desvio = statistics.stdev(resultados)
    else:
        desvio = 0.0

    return melhor_solucao, menor_custo, media, desvio, melhor_energia

# Pega o caminho de coordenadas do A* e descobre a sequencia exata em que os ginasios foram visitados
def extrair_ordem_ginasios(caminho, mapa):
    ordem = []
    visitados = set()
    
    for passo in caminho:
        x = passo[0]
        y = passo[1]
        celula = mapa[x][y]
        
        if celula in DIFICULDADE_GINASIOS:
            if celula not in visitados:
                ordem.append(celula)
                visitados.add(celula)
                
    return ordem

def main():
    arquivo = open("mapa.txt", "r")
    string_mapa = arquivo.read()
    arquivo.close()
    
    mapa = carregar_mapa(string_mapa)
    
    inicio, destino = encontrar_inicio_e_destino(mapa)
    if inicio is None or destino is None:
        print("Erro: Origem (1) ou Destino (U) não encontrados no mapa.")
        return

    print("A calcular a melhor rota com A*...")
    caminho, custo_rota = busca_a_estrela(mapa, inicio, destino)
    
    if caminho is None:
        print("Não foi possível encontrar uma rota válida.")
        return

    ordem_ginasios = extrair_ordem_ginasios(caminho, mapa)
    
    print("\nA otimizar as batalhas...")
    num_testes = 30
    melhor_resultado_global = None

    print("\n[1/3] A executar Hill Climbing...")
    solucao_hc, custo_hc, media_hc, desvio_hc, energia_hc = executar_experimentos(
        "Hill Climbing", lambda og: hill_climbing(og, iteracoes=1000), ordem_ginasios, num_testes
    )
    print("Testes: " + str(num_testes) + " | Média: " + f"{media_hc:.2f}" + " | Desvio: " + f"{desvio_hc:.2f}" + " | Melhor Custo: " + f"{custo_hc:.2f}")

    if melhor_resultado_global is None or custo_hc < melhor_resultado_global['custo']:
        melhor_resultado_global = {
            'algoritmo': "Hill Climbing", 
            'solucao': solucao_hc, 
            'custo': custo_hc, 
            'energia': energia_hc
        }
        
    print("\n[2/3] A executar Simulated Annealing...")
    solucao_sa, custo_sa, media_sa, desvio_sa, energia_sa = executar_experimentos(
        "Simulated Annealing", lambda og: simulated_annealing(og, iteracoes=1000), ordem_ginasios, num_testes
    )
    print("Testes: " + str(num_testes) + " | Média: " + f"{media_sa:.2f}" + " | Desvio: " + f"{desvio_sa:.2f}" + " | Melhor Custo: " + f"{custo_sa:.2f}")

    if melhor_resultado_global is None or custo_sa < melhor_resultado_global['custo']:
        melhor_resultado_global = {
            'algoritmo': "Simulated Annealing", 
            'solucao': solucao_sa, 
            'custo': custo_sa, 
            'energia': energia_sa
        }

    print("\n[3/3] A executar Algoritmo Genético...")
    solucao_ag, custo_ag, media_ag, desvio_ag, energia_ag = executar_experimentos(
        "Algoritmo Genético", lambda og: algoritmo_genetico(og, geracoes=50), ordem_ginasios, num_testes
    )
    print("Testes: " + str(num_testes) + " | Média: " + f"{media_ag:.2f}" + " | Desvio: " + f"{desvio_ag:.2f}" + " | Melhor Custo: " + f"{custo_ag:.2f}")

    if melhor_resultado_global is None or custo_ag < melhor_resultado_global['custo']:
        melhor_resultado_global = {
            'algoritmo': "Algoritmo Genético", 
            'solucao': solucao_ag, 
            'custo': custo_ag, 
            'energia': energia_ag
        }

    custo_total = custo_rota + melhor_resultado_global['custo']
    
    print("\n" + "="*40)
    print("RESULTADOS FINAIS OBRIGATÓRIOS")
    print("="*40)
    print("Melhor Algoritmo de Batalha: " + melhor_resultado_global['algoritmo'])
    print("Ordem de visita aos 24 ginásios: " + str(ordem_ginasios))
    print("Pokémon usados em cada batalha: " + str(melhor_resultado_global['solucao']))
    print("Energia final de cada Pokémon: " + str(melhor_resultado_global['energia']))
    print("Custo das Batalhas: " + f"{melhor_resultado_global['custo']:.2f}" + " minutos")
    print("Custo da Rota: " + str(custo_rota) + " minutos")
    print("Custo Total (C_total): " + f"{custo_total:.2f}" + " minutos")

if __name__ == "__main__":
    main()