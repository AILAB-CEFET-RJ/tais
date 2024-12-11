import json
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import pandas as pd
from services.file_service import normalize_timestamps
from flask import Response,jsonify

def calculate_heatmap_data():

    f = open('resources/recorte_data.json')
    
    data = json.load(f)

    f.close()
    
    coordenadas_embarcacao = np.empty((0, 2))

    for i in data:
        latitude = i["cinematica"]["posicao"]["geo"]["lat"]
        longitude = i["cinematica"]["posicao"]["geo"]["lng"]
        coordenada = np.array([[latitude, longitude]])
        coordenadas_embarcacao = np.append(coordenadas_embarcacao, coordenada, axis=0)
  
    lat_min, lat_max = coordenadas_embarcacao[:, 0].min(), coordenadas_embarcacao[:, 0].max()
    lon_min, lon_max = coordenadas_embarcacao[:, 1].min(), coordenadas_embarcacao[:, 1].max()

    resolution = 100
    lat_grid = np.linspace(lat_min, lat_max, resolution)
    lon_grid = np.linspace(lon_min, lon_max, resolution)
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
    grid_points = np.vstack([lat_mesh.ravel(), lon_mesh.ravel()])
    
    kde = gaussian_kde(coordenadas_embarcacao.T, bw_method='silverman')
    density:np.ndarray = kde(grid_points)
    density = density.reshape(lat_mesh.shape)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(density.T, origin='lower', extent=[lat_min, lat_max, lon_min, lon_max], cmap='hot', aspect='auto')
    plt.colorbar(label='Density')
    plt.title('Mapa de Calor das Rotas da Embarcação')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.show()

    return density.tolist() # retornar sem tolist permite visualizar o heatmap, mas causa problemas com o Docker


def calculate_heatmap_data_from_csv(csv_file_path, vessel_id=None, start_time=None, end_time=None, bbox=None)->Response:
    column_names = [
        'vesselId', 'long', 'lat', 'rumo', 
        'velocidade', 'timestamp'
    ]
    
    try:
        df = pd.read_csv(csv_file_path, header=None, names=column_names)
        print(df.head())
        print(df.columns)
    except Exception as e:
        print(f"Erro ao carregar o arquivo CSV: {e}")
        return {"error": f"Erro ao carregar o arquivo CSV: {str(e)}"}

    df = normalize_timestamps(df) # remover os milissegundos das datas pra n ocorrer erros

    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        print(df['timestamp'].head())
        print(df.dtypes)
        if df['timestamp'].isna().any():
            print("Valores inválidos encontrados após conversão:")
            print(df[df['timestamp'].isna()])
    except Exception as e:
        print(f"Erro ao converter 'timestamp': {e}")
        return {"error": f"Erro ao converter 'timestamp': {str(e)}"}

    print(df[df['timestamp'].isna()])  # ve se algum valor ficou como na

    if vessel_id:
        df = df[df['vesselId'] == vessel_id]

    if start_time and end_time:
        try:
            start_time = pd.to_datetime(start_time, format='%Y-%m-%d %H:%M:%S')
            end_time = pd.to_datetime(end_time, format='%Y-%m-%d %H:%M:%S')

            df['timestamp'] = df['timestamp'].dt.floor('S')
            start_time = max(start_time, df['timestamp'].min())
            end_time = min(end_time, df['timestamp'].max())

            df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]
            print(f"Filtrando entre {start_time} e {end_time}")
        except Exception as e:
            print(f"Erro ao filtrar pelo intervalo de tempo: {e}")
            return {"error": f"Erro ao filtrar pelo intervalo de tempo: {str(e)}"}

        
    # filtra pela bounding box se tiver
    if bbox:
        print("Recebido bbox:", bbox)
        lat_min, lon_min, lat_max, lon_max = bbox
        df = df[(df['lat'] >= lat_min) & (df['lat'] <= lat_max) & (df['long'] >= lon_min) & (df['long'] <= lon_max)]

    if df.empty or 'lat' not in df.columns or 'long' not in df.columns:
        print("Nenhum dado válido encontrado no intervalo especificado.")
        return {"error": "Nenhum dado válido encontrado no intervalo especificado."}
    
    # filtra dados com velocidade 0
    df = df[df["velocidade"]>0]

    coordenadas_embarcacao = df[['lat', 'long']].to_numpy()

    lat_min, lat_max = coordenadas_embarcacao[:, 0].min(), coordenadas_embarcacao[:, 0].max()
    lon_min, lon_max = coordenadas_embarcacao[:, 1].min(), coordenadas_embarcacao[:, 1].max()

    resolution = 100

    lat_grid = np.linspace(lat_min, lat_max, resolution)
    lon_grid = np.linspace(lon_min, lon_max, resolution)
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
    grid_points = np.vstack([lat_mesh.ravel(), lon_mesh.ravel()])

    kde = gaussian_kde(coordenadas_embarcacao.T, bw_method='silverman')
    density: np.ndarray = kde(grid_points)
    density = density.reshape(lat_mesh.shape)
    
    return jsonify({
        "density_array":density.T.tolist(),
        "min_latitude":lat_min,
        "max_latitude":lat_max,
        "min_longitude":lon_min,
        "max_longitude":lon_max,
        "vel":df["velocidade"].tolist()
        })
