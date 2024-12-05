from flask import Blueprint, request, Response
from routes.heatmap import get_heatmap_from_csv
from matplotlib import pyplot as plt
import io

visualization_bp = Blueprint("visualization",__name__)

@visualization_bp.route("/", methods=["GET"])
def view_heatmap()->Response:
    data = get_heatmap_from_csv().json
    density=data["density_array"]
    lat_min=data["min_latitude"]
    lat_max=data["max_latitude"]
    lon_min=data["min_longitude"]
    lon_max=data["max_longitude"]
    fig = plt.figure(figsize=(10, 8)) # plotagem em si
    plt.imshow(density, origin='lower', extent=[lat_min, lat_max, lon_min, lon_max], cmap='hot', aspect='auto')
    plt.colorbar(label='Density')
    plt.title('Mapa de Calor das Rotas da Embarcação')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.show()
    
    img = io.BytesIO()
    plt.savefig(img, format='svg')
    img.seek(0)
    plt.close(fig)
    return Response(img.getvalue(),mimetype="image/svg+xml")