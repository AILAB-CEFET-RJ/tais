from flask import Blueprint, request, Response
import os
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from collections import defaultdict
from routes.routesmap import get_routesmap_from_csv
import seaborn as sns
import random
import colorsys

# Defina o caminho para salvar as imagens
IMAGE_SAVE_DIR = "img"
heatmap_bp = Blueprint("heatmap", __name__)

@heatmap_bp.route("/heatmap", methods=["GET"])
def view_routesmap_heatmap() -> Response:
    data = get_routesmap_from_csv().json
    coordinates = list((tuple(c) for c in data["coordinates"]))
    if coordinates is None or len(coordinates) == 0:
        return Response(f"Erro: {data['error']}", status=400)

    routes = {}
    for lat, lon, route_id in coordinates:
        routes.setdefault(route_id, []).append((lat, lon))

    lat_min, lat_max = data["min_latitude"], data["max_latitude"]
    lon_min, lon_max = data["min_longitude"], data["max_longitude"]

    bbox = request.args.get("bbox")
    if bbox:
        try:
            bbox = list(map(float, bbox.split(',')))
            assert len(bbox) == 4
            lat_min, lon_min, lat_max, lon_max = bbox
        except (ValueError, AssertionError) as e:
            return Response(f"Erro no formato da bounding box: {str(e)}", status=400)
        lat_padding = lon_padding = 0
    else:
        padding = max(lat_max - lat_min, lon_max - lon_min) / 4
        lat_padding = lon_padding = padding

    # Densidade por célula (bucket de ~100m)
    density_map = defaultdict(int)
    for lat, lon, _ in coordinates:
        lat_b = round(lat / 0.001) * 0.001
        lon_b = round(lon / 0.001) * 0.001
        density_map[(lat_b, lon_b)] += 1

    # Preparar heatmap
    fig = plt.figure(figsize=(12, 14))
    try:
        ax = plt.axes(projection=ccrs.Miller())
        ax.set_extent([lon_min - lon_padding, lon_max + lon_padding,
                       lat_min - lat_padding, lat_max + lat_padding], crs=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND, facecolor='lightgreen')
        ax.add_feature(cfeature.OCEAN, facecolor='blue')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)
        ax.add_feature(cfeature.STATES, linestyle='--', linewidth=0.5)
        # Paleta 
        cmap = plt.cm.hot  
        all_counts = list(density_map.values())
        global_norm = plt.Normalize(vmin=min(all_counts), vmax=max(all_counts))

        # Pode definir máximo de rotas
        for route_id, route_coords in list(routes.items())[:500]:
            lats, lons = zip(*route_coords)
            route_densities = [
                density_map[(round(lat / 0.001) * 0.001, round(lon / 0.001) * 0.001)]
                for lat, lon in route_coords
            ]

            for i in range(len(route_coords) - 1):
                density = route_densities[i]
                color = cmap(global_norm(density))
                ax.plot(lons[i:i+2], lats[i:i+2], color=color, alpha=0.4,
                        transform=ccrs.PlateCarree(), linewidth=1.5, zorder=5)

        # Barra de cor
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=global_norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, orientation='vertical', label="Densidade de Passagens")

        plt.title("Mapa de Calor de Rotas de Embarcação", fontsize=20)
        plt.xlabel("Longitude", fontsize=14)
        plt.ylabel("Latitude", fontsize=14)

        os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
        image_path = os.path.join(IMAGE_SAVE_DIR, "heatmap_routes.svg")
        plt.savefig(image_path, format="svg")

        img = io.BytesIO()
        plt.savefig(img, format="svg")
        img.seek(0)
    finally:
        plt.close(fig)

    return Response(img.getvalue(), mimetype="image/svg+xml")