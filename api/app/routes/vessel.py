from flask import Blueprint
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
