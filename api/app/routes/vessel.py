from flask import Blueprint, jsonify
from services.vessel_service import getVessel, filter_by_timestamp_range
from services.file_service import convert_df_to_json

vessel_bp = Blueprint("vessel", __name__)

@vessel_bp.route("/<string:vessel_id>", methods=["GET"])
def get_vessel(vessel_id):
    df = getVessel("sorted_historico_acompanhamentos_24horas.csv", vessel_id)
    if isinstance(df, tuple):
        return df
    return convert_df_to_json(df)

@vessel_bp.route("/timestamp/<string:init>/<string:end>", methods=["GET"])
def filter_timestamp(init, end):
    df = filter_by_timestamp_range("sorted_historico_acompanhamentos_24horas.csv", init, end)
    return convert_df_to_json(df)

# @app.route('/api/data', methods=['GET'])
# def get_data():
#     combined_data = []
#     dir_path = '../data/cinematicas/' # MUDAR O DIRETÓRIO

#     for path in os.listdir(dir_path):
#         for archive in os.listdir(dir_path + path):
#             newDir = os.path.join(dir_path, path, archive)
#             if os.path.isfile(newDir):
#                 with open(newDir, 'r') as file:
#                     data = json.load(file)
#                     combined_data.append(data)

#     output_file = 'tais_data.json'
#     with open(output_file, 'w') as file:
#         json.dump(combined_data, file, indent=4) 

#     print("Arquivo combinado salvo com sucesso!")
#     f = open('tais_data.json')
#     data = json.load(f)

#     return data