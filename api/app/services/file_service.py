import pandas as pd
import json

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
            json_data.append(entry)
    return json.dumps(json_data, indent=4)

def normalize_timestamps(df): #! usada em calculate_heatmap_data_from_csv
    try:
        # remover milissegundos se tiver
        df['timestamp'] = df['timestamp'].astype(str).str.split('.').str[0]
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce') # tira ms
        
        print("Timestamps normalizados:")
        print(df['timestamp'].head())
    except Exception as e:
        print(f"Erro ao normalizar timestamps: {e}")
        return {"error": f"Erro ao normalizar timestamps: {str(e)}"}
    
    return df