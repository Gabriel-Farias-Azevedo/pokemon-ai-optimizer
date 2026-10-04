CUSTOS_TERRENO = {
    'M': 200, 
    'A': 30,  
    'F': 15,  
    'R': 5,   
    '.': 1,   
    '1': 1,   
    'U': 1    
}

DIFICULDADE_GINASIOS = {
    '2': 35, '3': 40, '4': 45, '5': 50, '6': 55, '7': 60, '8': 65, '9': 70,
    'B': 75, 'C': 80, 'D': 85, 'E': 90, 'G': 95, 'H': 100, 'I': 110, 'J': 120,
    'K': 130, 'L': 140, 'N': 150, 'O': 155, 'P': 160, 'Q': 165, 'S': 170, 'T': 180
}

POKEMONS = {
    'Pikachu': {'poder': 1.5, 'energia': 6},
    'Bulbassauro': {'poder': 1.4, 'energia': 6},
    'Rattata': {'poder': 1.3, 'energia': 6},
    'Caterpie': {'poder': 1.2, 'energia': 6},
    'Weedle': {'poder': 1.1, 'energia': 6}
}

# Transforma o texto gigante do mapa em uma matriz (lista de listas) para facilitar o acesso
def carregar_mapa(string_mapa):
    linhas_texto = string_mapa.strip().split('\n')
    matriz_mapa = []
    
    for linha in linhas_texto:
        caracteres_da_linha = list(linha)
        matriz_mapa.append(caracteres_da_linha)
        
    return matriz_mapa

# Devolve o custo de tempo para pisar em uma celula especifica do mapa.
# Se for um ginasio, o custo de movimento é livre (1), pois o tempo da batalha é somado depois.
def obter_custo_movimento(celula):
    if celula in CUSTOS_TERRENO:
        custo = CUSTOS_TERRENO[celula]
        return custo
    elif celula in DIFICULDADE_GINASIOS:
        return 1
    else:
        # Custo padrao caso venha algum caractere estranho
        return 1