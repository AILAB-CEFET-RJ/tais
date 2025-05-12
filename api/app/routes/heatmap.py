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
import random
import pandas as pd
# Defina o caminho para salvar as imagens
IMAGE_SAVE_DIR = "img"
heatmap_bp = Blueprint("heatmap", __name__)

#def gerar_dados_ficticios_varias_rotas(coords, qtd_rotas=2, qtd_variacoes=20):
#    dados_ficticios = []

#    for rota_id in range(1, qtd_rotas + 1):
#        deslocamento_lat = rota_id * 0.2
#        deslocamento_lon = rota_id * 0.2

#        for lat, lon, _ in coords:
#            for _ in range(qtd_variacoes):
#                lat_ficticio = lat + deslocamento_lat + random.uniform(-0.05, 0.05)
 ##              dados_ficticios.append((lat_ficticio, lon_ficticio, rota_id))

   # df_ficticio = pd.DataFrame(dados_ficticios, columns=["lat", "long", "vesselId"])

    #return {
     #   "coordinates": list(zip(df_ficticio["lat"], df_ficticio["long"], df_ficticio["vesselId"])),
      ## "max_latitude": df_ficticio["lat"].max(),
        #"min_longitude": df_ficticio["long"].min(),
        #"max_longitude": df_ficticio["long"].max()
    #}
def gerar_dados_ficticios_varias_rotas(coords, qtd_variacoes=1):
    dados_ficticios = []

    for lat, lon, _ in coords:
        for _ in range(qtd_variacoes):
            lat_ficticio = lat + random.uniform(-0.005, 0.005)  # variação menor (~500m)
            lon_ficticio = lon + random.uniform(-0.005, 0.005)
            dados_ficticios.append((lat_ficticio, lon_ficticio, 0))  # rota_id sempre 0

    df_ficticio = pd.DataFrame(dados_ficticios, columns=["lat", "long", "vesselId"])

    return {
        "coordinates": list(zip(df_ficticio["lat"], df_ficticio["long"], df_ficticio["vesselId"])),
        "min_latitude": df_ficticio["lat"].min(),
        "max_latitude": df_ficticio["lat"].max(),
        "min_longitude": df_ficticio["long"].min(),
        "max_longitude": df_ficticio["long"].max()
    }

@heatmap_bp.route("/heatmap", methods=["GET"])
def view_routesmap_heatmap() -> Response:
    from routes.routesmap import get_routesmap_from_csv
    data = get_routesmap_from_csv().json

    coordinates = [(*c, 0) if len(c) == 2 else tuple(c) for c in data.get("coordinates", [])]

    if not coordinates:
        return Response("Erro: Nenhuma coordenada recebida", status=400)

    ficticio_data = gerar_dados_ficticios_varias_rotas(coordinates, qtd_variacoes=1)
    coordinates = ficticio_data["coordinates"]

    lat_min, lat_max = ficticio_data["min_latitude"], ficticio_data["max_latitude"]
    lon_min, lon_max = ficticio_data["min_longitude"], ficticio_data["max_longitude"]

    if lat_min >= lat_max or lon_min >= lon_max:
        return Response("Erro: limites geográficos inválidos", status=400)

    # Agrupa por rota ID
    routes = {}
    for lat, lon, route_id in coordinates:
        routes.setdefault(route_id, []).append((lat, lon))

    # Bounding box opcional
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

    # Mapa de densidade
    density_map = defaultdict(int)
    for lat, lon, _ in coordinates:
        lat_b = round(lat / 0.001) * 0.001
        lon_b = round(lon / 0.001) * 0.001
        density_map[(lat_b, lon_b)] += 1

    all_counts = list(density_map.values())
    if not all_counts:
        return Response("Erro: mapa de densidade vazio", status=400)

    vmin = 1
    vmax = np.percentile(all_counts, 99)
    if vmax <= vmin:
        vmax = vmin + 1

    global_norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.inferno

    # Plot
    fig = plt.figure(figsize=(12, 14))
    try:
        ax = plt.axes(projection=ccrs.Miller())
        ax.set_extent([lon_min - lon_padding, lon_max + lon_padding,
                       lat_min - lat_padding, lat_max + lat_padding], crs=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='lightgreen')
        ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='blue')
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.5)
        ax.add_feature(cfeature.STATES.with_scale('50m'), linestyle='--', linewidth=0.5)

        for route_coords in routes.values():
            lats, lons = zip(*route_coords)
            route_densities = [
                density_map[(round(lat / 0.001) * 0.001, round(lon / 0.001) * 0.001)]
                for lat, lon in route_coords
            ]

            for i in range(len(route_coords) - 1):
                density = route_densities[i]
                color = cmap(global_norm(density))
                ax.plot(lons[i:i+2], lats[i:i+2], color=color, alpha=0.9,
                        transform=ccrs.PlateCarree(), linewidth=1.5, zorder=5)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=global_norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, orientation='vertical', label="Densidade de Passagens")

        plt.title("Mapa de Calor de Rotas de Embarcação", fontsize=20)

        os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
        image_path = os.path.join(IMAGE_SAVE_DIR, "heatmap_routes.svg")
        plt.savefig(image_path, format="svg")

        img = io.BytesIO()
        plt.savefig(img, format="svg")
        img.seek(0)
    finally:
        plt.close(fig)

    return Response(img.getvalue(), mimetype="image/svg+xml")
