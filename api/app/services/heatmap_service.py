import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import pandas as pd
from services.file_service import normalize_timestamps
from flask import Response,jsonify,request

def calculate_heatmap_data_from_csv(csv_file_path, vessel_id=None, start_time=None, end_time=None, bbox=None) -> Response:
    column_names = [
        'vesselId', 'long', 'lat', 'rumo', 
        'velocidade', 'timestamp'
    ]
    
    try:
        df = pd.read_csv(csv_file_path, header=None, names=column_names)
    except Exception as e:
        return {"error": f"Erro ao carregar o arquivo CSV: {str(e)}"}

    df = normalize_timestamps(df) # remover os milissegundos das datas pra n ocorrer erros
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce') # Converter timestamp para datetime

    if vessel_id:
        df = df[df['vesselId'] == vessel_id]
    
    if start_time and end_time: # filtra por intervalo de tempo
        start_time = pd.to_datetime(start_time, format='%Y-%m-%d %H:%M:%S')
        end_time = pd.to_datetime(end_time, format='%Y-%m-%d %H:%M:%S')
        df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]

    if bbox:
        # filtrar o dataframe de forma a incluir apenas os pontos da bbox que a gente quer
        lat_min, lon_min, lat_max, lon_max = map(float, bbox.split(','))
        df = df[(df['lat'] >= lat_min) & (df['lat'] <= lat_max) &
                (df['long'] >= lon_min) & (df['long'] <= lon_max)]
    else:
        lat_min, lat_max = df['lat'].min(), df['lat'].max()
        lon_min, lon_max = df['long'].min(), df['long'].max()

    df = df[df["velocidade"] > 0] # remove embarcacoes paradas

    # Coordenadas da embarcação
    coordenadas_embarcacao = df[['lat', 'long']].to_numpy()

    if coordenadas_embarcacao.size == 0: # ver se existem dados suficientes pra fazer um plot
        return jsonify({
            "error": "Nenhum dado válido encontrado para os filtros aplicados.",
            "density_array": [],
            "min_latitude": lat_min,
            "max_latitude": lat_max,
            "min_longitude": lon_min,
            "max_longitude": lon_max,
        })

    resolution = 150  # resolução do heatmap em si
    # aqui vai ajustar os limites do grid com base na bbox (se tiver)
    lat_grid = np.linspace(lat_min, lat_max, resolution)
    lon_grid = np.linspace(lon_min, lon_max, resolution)
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
    grid_points = np.vstack([lat_mesh.ravel(), lon_mesh.ravel()])

    # Calcular KDE com os pontos filtrados
    kde = gaussian_kde(coordenadas_embarcacao.T, bw_method='silverman')
    density = kde(grid_points) # nao usa mais um grid global
    density = density.reshape(lat_mesh.shape)

    return jsonify({
        "density_array": density.T.tolist(),  # Transposto para corresponder ao formato esperado
        "min_latitude": lat_min,
        "max_latitude": lat_max,
        "min_longitude": lon_min,
        "max_longitude": lon_max,
    })