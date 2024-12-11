from flask import jsonify
import pandas as pd
import os

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