from flask import Blueprint, request, Response
import os
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from collections import defaultdict
import random
import pandas as pd

IMAGE_SAVE_DIR = "img"
heatmap_bp = Blueprint("heatmap", __name__)

def gerar_dados_ficticios_varias_rotas(coords, qtd_variacoes=1):
    dados_ficticios = []
    for lat, lon, _ in coords:
        for _ in range(qtd_variacoes):
            lat_ficticio = lat + random.uniform(-0.005, 0.005)
            lon_ficticio = lon + random.uniform(-0.005, 0.005)
            dados_ficticios.append((lat_ficticio, lon_ficticio, 0))

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

    try:
        grid_param = request.args.get("grid", default="0.800")
        GRID_SIZE = float(grid_param)
    except ValueError:
        return Response("Erro: parâmetro 'grid' inválido. Use um número como 0.005", status=400)

    routes = {}
    for lat, lon, route_id in coordinates:
        routes.setdefault(route_id, []).append((lat, lon))

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

    density_map = defaultdict(int)
    for lat, lon, _ in coordinates:
        lat_b = round(lat / GRID_SIZE) * GRID_SIZE
        lon_b = round(lon / GRID_SIZE) * GRID_SIZE
        density_map[(lat_b, lon_b)] += 1

    all_counts = list(density_map.values())
    if not all_counts:
        return Response("Erro: mapa de densidade vazio", status=400)

    vmin = np.percentile(all_counts, 10)
    vmax = np.percentile(all_counts, 98)
    if vmax <= vmin:
        vmax = vmin + 1

    global_norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.inferno

    fig = plt.figure(figsize=(12, 14))
    try:
        ax = plt.axes(projection=ccrs.Miller())
        ax.set_extent([lon_min - lon_padding, lon_max + lon_padding,
                       lat_min - lat_padding, lat_max + lat_padding], crs=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='#0a0a0a')
        ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='#001f3f')
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.5)
        ax.add_feature(cfeature.STATES.with_scale('50m'), linestyle='--', linewidth=0.5)

        for route_coords in routes.values():
            segments = []
            colors = []
            for i in range(len(route_coords) - 1):
                lat1, lon1 = route_coords[i]
                lat2, lon2 = route_coords[i + 1]
                segments.append([(lon1, lat1), (lon2, lat2)])
                lat_bin = round(lat1 / GRID_SIZE) * GRID_SIZE
                lon_bin = round(lon1 / GRID_SIZE) * GRID_SIZE
                density = density_map[(lat_bin, lon_bin)]
                colors.append(cmap(global_norm(density)))

            lc = LineCollection(segments, colors=colors, linewidths=1.5, alpha=0.9,
                                transform=ccrs.PlateCarree(), zorder=5)
            ax.add_collection(lc)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=global_norm)
        sm.set_array([])
        cb = plt.colorbar(sm, ax=ax, orientation='vertical', label="Densidade de Passagens", shrink=0.7, pad=0.05)
        cb.ax.set_facecolor('#111111')
        cb.outline.set_edgecolor('white')
        cb.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='white')

        plt.title("Mapa de Calor de Rotas de Embarcação", fontsize=20, color='white')

        os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
        image_path = os.path.join(IMAGE_SAVE_DIR, "heatmap_routes.svg")
        plt.savefig(image_path, format="svg", facecolor='#000000')

        img = io.BytesIO()
        plt.savefig(img, format="svg", facecolor='#000000')
        img.seek(0)
    finally:
        plt.close(fig)

    return Response(img.getvalue(), mimetype="image/svg+xml")
