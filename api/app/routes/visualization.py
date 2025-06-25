import os
import matplotlib
matplotlib.use("Agg")  # Define o backend para uso não interativo
import matplotlib.pyplot as plt
import io
from flask import Response, Blueprint, request
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import colorsys
from random import random
from routes.routesmap import get_routesmap_from_csv

# Diretório para salvar imagem
IMAGE_SAVE_DIR = "img"

visualization_bp = Blueprint("visualization", __name__)

@visualization_bp.route("/", methods=["GET"])
def view_routesmap() -> Response:
    # Obtém os dados do CSV
    data = get_routesmap_from_csv().json
    coordinates = list((tuple(c) for c in data["coordinates"]))

    if not coordinates:
        return Response(f"Erro: {data['error']}", status=400)

    routes = {}
    for line in coordinates:
        if line[2] in routes:
            routes[line[2]].append((line[0], line[1]))
        else:
            routes[line[2]] = [(line[0], line[1])]
            
    # Obtem os limites geográficos
    lat_min = data["min_latitude"]
    lat_max = data["max_latitude"]
    lon_min = data["min_longitude"]
    lon_max = data["max_longitude"]

    # Processa bounding box
    bbox = request.args.get("bbox")
    if bbox:
        try:
            bbox = list(map(float, bbox.split(',')))
            assert len(bbox) == 4, "Bounding box deve conter 4 valores"
            lat_min, lon_min, lat_max, lon_max = bbox
            assert lat_min < lat_max and lon_min < lon_max
        except Exception as e:
            return Response(f"Erro no formato da bounding box: {str(e)}", status=400)
        lat_padding, lon_padding = 0, 0
    else:
        lat_padding = (lat_max - lat_min) / 4
        lon_padding = (lon_max - lon_min) / 4

    # Cria a imagem
    fig = plt.figure(figsize=(10, 10))
    try:
        ax = plt.axes(projection=ccrs.Miller())
        ax.set_extent([lon_min - lon_padding, lon_max + lon_padding,
                       lat_min - lat_padding, lat_max + lat_padding], crs=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND, facecolor='lightgreen')
        ax.add_feature(cfeature.OCEAN, facecolor='blue')
        ax.add_feature(cfeature.COASTLINE, linewidth=1)
        ax.add_feature(cfeature.BORDERS, linewidth=3)
        ax.add_feature(cfeature.STATES, linestyle='--')

        for id, coords in routes.items():
            color = [random(), random(), random()]
            while color[0] >= 0.5 and color[0] < 0.7:
                color[0] = random()
            while color[1] < 0.7:
                color[1] = random()
            while color[2] < 0.5:
                color[2] = random()
            color = colorsys.hsv_to_rgb(*color)

            lats, lons = zip(*coords)
            ax.plot(lons, lats, color=color, transform=ccrs.PlateCarree(), linewidth=1, zorder=5)

        plt.title("Mapa de Rotas de Embarcação", fontsize=24)
        plt.xlabel("Longitude", fontsize=20)
        plt.ylabel("Latitude", fontsize=20)

        os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
        image_path = os.path.join(IMAGE_SAVE_DIR, "routes.svg")
        plt.savefig(image_path, format="svg")

        img = io.BytesIO()
        plt.savefig(img, format="svg")
        img.seek(0)

    finally:
        plt.close(fig)

    return Response(img.getvalue(), mimetype="image/svg+xml")
