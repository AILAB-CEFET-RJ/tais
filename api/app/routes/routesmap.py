from flask import Blueprint, request, Response
from services.routesmap_service import calculate_routesmap_data_from_csv

routesmap_bp = Blueprint("routesmap", __name__)

@routesmap_bp.route("/routesmap_csv", methods=["GET"])
def get_routesmap_from_csv():
    csv_file = "resources/dataset-09-29-recorte.csv"
    #csv_file = "resources/ship_trajectory.csv"
    # csv_file = "resources/single_t_data/IHS-AIS-256298000.csv"
    #csv_file = "resources/single_t_data/IHS-AIS-255915766.csv"
    vessel_id = request.args.get("vesselId")
    start_time = request.args.get("startTime")
    end_time = request.args.get("endTime")
    bbox = request.args.get("bbox")
    print("Recebido bbox:", bbox)

    response = calculate_routesmap_data_from_csv(csv_file, vessel_id, start_time, end_time, bbox)
    coordinates = list((tuple(c) for c in response.json["coordinates"]))
    if coordinates is None or len(coordinates) == 0:
        return Response(f"Erro: {response['error']}", status=400)
    else:
        return response
