import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pandas as pd
from geopy.distance import geodesic
import json
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API de análise de trajetórias de embarcações"

@app.route('/api/data', methods=['GET'])
def get_data():
    # Lista para armazenar os dados combinados
    combined_data = []
    dir_path = '../data/cinematicas/' # MUDAR O DIRETÓRIO

    for path in os.listdir(dir_path):
        
        for archive in os.listdir(dir_path + path):
            newDir = os.path.join(dir_path, path, archive)
            if os.path.isfile(newDir):
                with open(newDir, 'r') as file:
                    # Ler o conteúdo do arquivo JSON e converter para um dicionário Python
                    data = json.load(file)
                    # Adicionar os dados do arquivo atual à lista combinada
                    combined_data.append(data)

    # Caminho onde você deseja salvar o arquivo JSON combinado
    output_file = 'tais_data.json'

    # Escrever os dados combinados em um único arquivo JSON
    with open(output_file, 'w') as file:
        json.dump(combined_data, file, indent=4) 

    print("Arquivo combinado salvo com sucesso!")
    f = open('tais_data.json')
    data = json.load(f)

    return data

@app.route('/api/heatmap', methods=['GET'])
def get_heatmap_data():

    return calculate_heatmap_data()

@app.route('/api/heatmap_csv', methods=['GET'])
def get_heatmap_from_csv():
    csv_file = "recorte_dados.csv"
    vessel_id = request.args.get('vesselId')
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    
    return calculate_heatmap_data_from_csv(csv_file, vessel_id, start_time, end_time)


@app.route('/vessel/<string:vessel_id>', methods=['GET'])
def get_vessel(vessel_id):
    df = getVessel("sorted_historico_acompanhamentos_24horas.csv", vessel_id)
    if isinstance(df, tuple):
        return df  
    return convert_df_to_json(df)

@app.route('/timestamp/<string:init>/<string:end>', methods=['GET'])
def filter_timestamp(init, end):
    df = filter_by_timestamp_range("sorted_historico_acompanhamentos_24horas.csv", init, end)
    return convert_df_to_json(df)

def calculate_heatmap_data():

    f = open('tais_data.json')
    
    data = json.load(f)

    f.close()
    
    coordenadas_embarcacao = np.empty((0, 2))

    for i in data:
        latitude = i["cinematica"]["posicao"]["geo"]["lat"]
        longitude = i["cinematica"]["posicao"]["geo"]["lng"]
        coordenada = np.array([[latitude, longitude]])
        coordenadas_embarcacao = np.append(coordenadas_embarcacao, coordenada, axis=0)
  
    # Limites das coordenadas (latitude e longitude)
    lat_min, lat_max = coordenadas_embarcacao[:, 0].min(), coordenadas_embarcacao[:, 0].max()
    lon_min, lon_max = coordenadas_embarcacao[:, 1].min(), coordenadas_embarcacao[:, 1].max()

    # Definir a resolução da grade (número de pontos na grade)
    resolution = 100

    # Criar grade de coordenadas
    lat_grid = np.linspace(lat_min, lat_max, resolution)
    lon_grid = np.linspace(lon_min, lon_max, resolution)
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
    grid_points = np.vstack([lat_mesh.ravel(), lon_mesh.ravel()])

    # Calcular KDE
    kde = gaussian_kde(coordenadas_embarcacao.T, bw_method='silverman')
    density:np.ndarray = kde(grid_points)
    density = density.reshape(lat_mesh.shape)

    # Plotar o mapa de calor
    plt.figure(figsize=(10, 8))
    plt.imshow(density.T, origin='lower', extent=[lat_min, lat_max, lon_min, lon_max], cmap='hot', aspect='auto')
    plt.colorbar(label='Density')
    plt.title('Mapa de Calor das Rotas da Embarcação')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.show()

    return density.tolist() # retornar sem tolist permite visualizar o heatmap, mas causa problemas com o Docker

def calculate_heatmap_data_from_csv(csv_file_path, vessel_id=None, start_time=None, end_time=None):
    """
    Gera um mapa de calor das trajetórias de embarcações a partir de um CSV sem cabeçalhos.
    
    Parâmetros:
        csv_file_path (str): Caminho do arquivo CSV.
        vessel_id (str, opcional): ID da embarcação para filtrar. Default: None (sem filtro).
        start_time (str, opcional): Data de início no formato 'YYYY-MM-DD HH:MM:SS'. Default: None.
        end_time (str, opcional): Data de término no formato 'YYYY-MM-DD HH:MM:SS'. Default: None.
    """
    # Definir os nomes das colunas
    column_names = [
        'vesselId', 'long', 'lat', 'rumo', 
        'velocidade', 'timestamp', 'origem', 'subOrigem'
    ]
    
    # Carregar o CSV sem cabeçalhos e definir os nomes das colunas
    try:
        df = pd.read_csv(csv_file_path, header=None, names=column_names)
        print(df.head())  # Exibe as primeiras linhas para debug
        print(df.columns)  # Lista todas as colunas para debug
    except Exception as e:
        print(f"Erro ao carregar o arquivo CSV: {e}")
        return {"error": f"Erro ao carregar o arquivo CSV: {str(e)}"}

    df = normalize_timestamps(df) # remover os milissegundos das datas

    try:
        # Converter tentando automaticamente detectar o formato
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Verifique o resultado após a conversão
        print(df['timestamp'].head())
        print(df.dtypes)
        
        # Identifique se restaram NaT
        if df['timestamp'].isna().any():
            print("Valores inválidos encontrados após conversão:")
            print(df[df['timestamp'].isna()])
    except Exception as e:
        print(f"Erro ao converter 'timestamp': {e}")
        return {"error": f"Erro ao converter 'timestamp': {str(e)}"}


    print(df[df['timestamp'].isna()])  # Verificar se algum valor ficou como NaT

    # Filtrar por ID da embarcação, se especificado
    if vessel_id:
        df = df[df['vesselId'] == vessel_id]

    # Filtrar pelo intervalo de tempo, se especificado
    if start_time and end_time:
        try:
            start_time = pd.to_datetime(start_time, format='%Y-%m-%d %H:%M:%S')
            end_time = pd.to_datetime(end_time, format='%Y-%m-%d %H:%M:%S')
            df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]
            print(f"Filtrando entre {start_time} e {end_time}")
        except Exception as e:
            print(f"Erro ao filtrar pelo intervalo de tempo: {e}")
            return {"error": f"Erro ao filtrar pelo intervalo de tempo: {str(e)}"}

    # Garantir que os dados de latitude e longitude estejam disponíveis
    if df.empty or 'lat' not in df.columns or 'long' not in df.columns:
        print("Nenhum dado válido encontrado no intervalo especificado.")
        return {"error": "Nenhum dado válido encontrado no intervalo especificado."}

    coordenadas_embarcacao = df[['lat', 'long']].to_numpy()

    # Limites das coordenadas (latitude e longitude)
    lat_min, lat_max = coordenadas_embarcacao[:, 0].min(), coordenadas_embarcacao[:, 0].max()
    lon_min, lon_max = coordenadas_embarcacao[:, 1].min(), coordenadas_embarcacao[:, 1].max()

    # Definir a resolução da grade (número de pontos na grade)
    resolution = 100

    # Criar grade de coordenadas
    lat_grid = np.linspace(lat_min, lat_max, resolution)
    lon_grid = np.linspace(lon_min, lon_max, resolution)
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
    grid_points = np.vstack([lat_mesh.ravel(), lon_mesh.ravel()])

    # Calcular KDE
    kde = gaussian_kde(coordenadas_embarcacao.T, bw_method='silverman')
    density: np.ndarray = kde(grid_points)
    density = density.reshape(lat_mesh.shape)

    # Plotar o mapa de calor
    plt.figure(figsize=(10, 8))
    plt.imshow(density.T, origin='lower', extent=[lat_min, lat_max, lon_min, lon_max], cmap='hot', aspect='auto')
    plt.colorbar(label='Density')
    plt.title('Mapa de Calor das Rotas da Embarcação')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.show()

    return density.tolist()


def normalize_timestamps(df):
    """
    Remove os milissegundos da coluna de timestamps para garantir uniformidade.
    """
    try:
        # Converter para string e remover milissegundos, se existirem
        df['timestamp'] = df['timestamp'].astype(str).str.split('.').str[0]
        
        # Converter de volta para datetime sem milissegundos
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Exibir os primeiros valores para debug
        print("Timestamps normalizados:")
        print(df['timestamp'].head())
    except Exception as e:
        print(f"Erro ao normalizar timestamps: {e}")
        return {"error": f"Erro ao normalizar timestamps: {str(e)}"}
    
    return df



def filter_by_timestamp_range(sorted_csv_file_path, start_timestamp, end_timestamp):
    chunksize = 100000

    chunk_list = []

    start_timestamp = pd.to_datetime(start_timestamp)
    end_timestamp = pd.to_datetime(end_timestamp)
    
    for chunk in pd.read_csv(sorted_csv_file_path, chunksize=chunksize):

        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], errors='coerce')
        
        chunk_filtered = chunk[(chunk['timestamp'] >= start_timestamp) & (chunk['timestamp'] <= end_timestamp)]
        
        chunk_list.append(chunk_filtered)

    df_filtered = pd.concat(chunk_list)

    df_filtered['timestamp'] = df_filtered['timestamp'].astype(str)

    return df_filtered

  
def getVessel(sorted_csv_file_path, vessel_id_filter):
    if not os.path.exists(sorted_csv_file_path):
        print(f"Arquivo ordenado {sorted_csv_file_path} não encontrado. Gerando o arquivo ordenado.")
        sortTimestamp("historico_acompanhamentos_24horas.csv", sorted_csv_file_path)

    chunksize = 100000
    chunk_list = []

    try:
        for chunk in pd.read_csv(sorted_csv_file_path, chunksize=chunksize):
            chunk_filtered = chunk[chunk['vesselId'] == vessel_id_filter]
            if not chunk_filtered.empty:
                chunk_list.append(chunk_filtered)

        if not chunk_list:
            return jsonify({"error": f"Embarcação com ID '{vessel_id_filter}' não encontrada."}), 404

        df_sorted_filtered = pd.concat(chunk_list)

    except Exception as e:
        print(f"Erro ao processar o arquivo CSV: {e}")
        return jsonify({"error": f"Erro ao processar o arquivo CSV: {str(e)}"}), 500

    return df_sorted_filtered

 
def sortTimestamp(csv_file_path, sorted_csv_file_path):
    chunksize = 100000

    chunk_list = []
    columns_to_load = [0, 1, 2, 5]
    column_names = ['vesselId','long', 'lat', 'timestamp']
    
    for chunk in pd.read_csv(csv_file_path,header=None, chunksize=chunksize, usecols=columns_to_load, names=column_names):
        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'],format='%Y-%m-%d %H:%M:%S', errors='coerce')
        chunk_sorted = chunk.sort_values(by='timestamp')
        chunk_list.append(chunk_sorted)

    df_sorted = pd.concat(chunk_list)
    df_sorted = df_sorted.sort_values(by='timestamp')
    df_sorted.to_csv(sorted_csv_file_path, index=False)

def convert_df_to_json(df):
    json_data = []
   
    for index, row in df.iterrows():
           
            entry = {
                "cinematica": {
                    "timestamp": row["timestamp"],
                    "vesselId":row["vesselId"],
                    "posicao": {
                        "geo": {
                            "lat": row["lat"],
                            "lng": row["long"]
                        }
                    }
                }
            }
           
            # Adicionando a entrada à lista JSON
            json_data.append(entry)

    # Convertendo a lista para JSON formatado
    return json.dumps(json_data, indent=4)
  

if __name__ == '__main__':
    app.run(debug=True)