import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import csv

def interpolar_pontos_com_dados(nome, pontos, intervalo_em_segundos):
    """
    Interpola uma lista de pontos geográficos e calcula velocidade e ângulo.

    Args:
        nome (str): Nome associado aos pontos.
        pontos (list of dict): Lista de pontos com 'latitude', 'longitude' e 'tempo' (formato 'AAAA-MM-DD HH:MM:SS').
        intervalo_em_segundos (int): Intervalo de tempo fixo para a interpolação (em segundos).

    Returns:
        list of dict: Lista de pontos interpolados com 'nome', 'latitude', 'longitude', 'tempo', 'velocidade' e 'ângulo'.
    """
    # Criar DataFrame com os pontos fornecidos
    df = pd.DataFrame(pontos)
    df['tempo'] = pd.to_datetime(df['tempo'])  # Converter para datetime

    # Garantir que os dados estão ordenados por tempo
    df = df.sort_values('tempo')

    # Criar o range de tempo fixo
    tempo_inicial = df['tempo'].iloc[0]
    tempo_final = df['tempo'].iloc[-1]
    novo_tempo = pd.date_range(start=tempo_inicial, end=tempo_final, freq=f"{intervalo_em_segundos}S")

    # Interpolação linear
    df = df.set_index('tempo')
    df_interpolado = df.reindex(novo_tempo).interpolate(method='linear').reset_index()
    df_interpolado.rename(columns={'index': 'tempo'}, inplace=True)

    # Calcular velocidade e ângulo
    R = 6371  # Raio da Terra em km
    df_interpolado['latitude_rad'] = np.radians(df_interpolado['latitude'])
    df_interpolado['longitude_rad'] = np.radians(df_interpolado['longitude'])

    # Distâncias entre pontos
    df_interpolado['delta_lat'] = df_interpolado['latitude_rad'].diff()
    df_interpolado['delta_lon'] = df_interpolado['longitude_rad'].diff()

    a = np.sin(df_interpolado['delta_lat'] / 2) ** 2 + \
        np.cos(df_interpolado['latitude_rad']) * np.cos(df_interpolado['latitude_rad'].shift()) * \
        np.sin(df_interpolado['delta_lon'] / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distancia_km = R * c
    distancia_milhas_nauticas = distancia_km * 0.539957  # Converter para milhas náuticas

    # Tempo em horas
    tempo_horas = df_interpolado['tempo'].diff().dt.total_seconds() / 3600

    # Velocidade em nós
    df_interpolado['velocidade'] = distancia_milhas_nauticas / tempo_horas

    # Ângulo em relação ao eixo x
    df_interpolado['angulo'] = np.degrees(
        np.arctan2(df_interpolado['delta_lon'], df_interpolado['delta_lat'])
    )

    # Ajustar ângulos negativos
    df_interpolado['angulo'] = (df_interpolado['angulo'] + 360) % 360

    # Adicionar o nome e formatar o tempo
    df_interpolado['nome'] = nome
    df_interpolado['tempo'] = df_interpolado['tempo'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Selecionar as colunas finais
    resultado = df_interpolado[['nome', 'latitude', 'longitude', 'tempo', 'velocidade', 'angulo']].to_dict(orient='records')
    return resultado

if __name__ == '__main__':
    # Exemplo de uso
    pontos_exemplo = [
        {"latitude": -23.5505, "longitude": -46.6333, "tempo": "2024-11-27 12:00:00"},
        {"latitude": -23.5510, "longitude": -46.6340, "tempo": "2024-11-27 12:05:00"},
        {"latitude": -23.5520, "longitude": -46.6350, "tempo": "2024-11-27 22:10:00"},
    ]

    resultado = interpolar_pontos_com_dados("IHS-TESTE", pontos_exemplo, 6)
    with open('teste.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        #escritor.writerow(['nome', 'latitude', 'longitude', 'angulo', 'velocidade', 'tempo'])
        for r in resultado:
            escritor.writerow([r['nome'], r['latitude'], r['longitude'], r['angulo'], r['velocidade'], r['tempo']])

    print("Arquivo CSV gerado")
