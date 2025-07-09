from flask import Blueprint, request, Response, jsonify
from services.routesmap_service import calculate_routesmap_data_from_csv

routesmap_bp = Blueprint("routesmap", __name__)

@routesmap_bp.route("/routesmap_csv", methods=["GET"])
def get_routesmap_from_csv():
    #csv_file = "resources/dataset-09-29-recorte.csv"
    #csv_file = "resources/ship_trajectory.csv"
    csv_file = "resources/single_t_data/IHS-AIS-256298000.csv"
    #csv_file = "resources/single_t_data/IHS-AIS-15.csv"
    #csv_file ="resources/single_t_data/combined_routes.csv"
    #csv_file = "resources/single_t_data/IHS-AIS-255915766.csv"
    #csv_file = "resources/single_t_data/combined_routes 1(in).csv"
    vessel_id = request.args.get("vesselId")
    start_time = request.args.get("startTime")
    end_time = request.args.get("endTime")
    bbox = request.args.get("bbox")
    vessel_type = request.args.get("vesselType")
    print("Recebido bbox:", bbox)

    response = calculate_routesmap_data_from_csv(csv_file, vessel_id, start_time, end_time, bbox, vessel_type)
    if not response.is_json:
        return jsonify({"error": "Resposta inesperada do serviço", "coordinates": []}), 500

    response_data = response.get_json()

    # Se houver erro já tratado pelo serviço, retorne direto
    if "error" in response_data:
        return jsonify(response_data), 400

    # Se passou, continue normalmente
    coordinates = list((tuple(c) for c in response_data["coordinates"]))
    if not coordinates:
        return jsonify({"error": "Nenhuma coordenada encontrada após os filtros.", "coordinates": []}), 400

    return jsonify(response_data)

    # response = calculate_routesmap_data_from_csv(csv_file, vessel_id, start_time, end_time, bbox, vessel_type)
    # coordinates = list((tuple(c) for c in response.json["coordinates"]))
    # if coordinates is None or len(coordinates) == 0:
    #     return Response(f"Erro: {response['error']}", status=400)
    # else:
    #     return response
