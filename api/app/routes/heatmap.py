from flask import Blueprint, request
from services.heatmap_service import calculate_heatmap_data, calculate_heatmap_data_from_csv

heatmap_bp = Blueprint("heatmap", __name__)

@heatmap_bp.route("/heatmap", methods=["GET"])
def get_heatmap():
    return calculate_heatmap_data()

@heatmap_bp.route("/heatmap_csv", methods=["GET"])
def get_heatmap_from_csv():
    csv_file = "resources/dataset-09-29-recorte.csv"
    #csv_file = "testee.csv"
    vessel_id = request.args.get("vesselId")
    start_time = request.args.get("startTime")
    end_time = request.args.get("endTime")

    bbox = request.args.get("bbox")
    if bbox:
        bbox = list(map(float, bbox.split(',')))  # Convertendo a string em uma lista de floats

    return calculate_heatmap_data_from_csv(csv_file, vessel_id, start_time, end_time)
