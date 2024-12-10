import os
import matplotlib.pyplot as plt
import io
from flask import Response
from routes.heatmap import get_heatmap_from_csv
from flask import Blueprint, request, Response
from mpl_toolkits.basemap import Basemap
import numpy as np

# Defina o caminho para salvar as imagens
IMAGE_SAVE_DIR = "img"
visualization_bp = Blueprint("visualization",__name__)

@visualization_bp.route("/", methods=["GET"])
def view_heatmap() -> Response:
    # Gera os dados do heatmap
    data = get_heatmap_from_csv().json
    density = np.array(data["density_array"])
    lat_min = data["min_latitude"]
    lat_max = data["max_latitude"]
    lon_min = data["min_longitude"]
    lon_max = data["max_longitude"]
    lat_padding = max(40-(lat_max - lat_min),0)/2
    lon_padding = max(40-(lon_max - lon_min),0)/2

    # Criação do heatmap
    fig = plt.figure(figsize=(50, 50))
    # criando recorte contendo rota encontrada, com no mínimo 40 graus em latitude e longitude, do mapa mundi usando projeção cilindrica de Miller
    mapamundi = Basemap(projection="mill",llcrnrlat=lat_min-lat_padding,llcrnrlon=lon_min-lon_padding,urcrnrlat=lat_max+lat_padding,urcrnrlon=lon_max+lon_padding)
    mapamundi.drawcoastlines(linewidth=3)
    mapamundi.drawcountries(linewidth=3)
    mapamundi.drawstates(linestyle="dashed")
    lons = np.linspace(lon_min, lon_max, len(density))
    lats = np.linspace(lat_min, lat_max, len(density[0]))
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    heatmap = mapamundi.pcolormesh(lon_grid,lat_grid, density, cmap='bwr', shading='auto',latlon=True)
    mapamundi.fillcontinents(color='lightgreen', lake_color='blue')
    mapamundi.drawmapboundary(fill_color="blue")
    # plt.imshow(density, origin="lower", extent=[lat_min, lat_max, lon_min, lon_max], cmap="hot", aspect="auto")
    escala = plt.colorbar(heatmap)
    escala.set_ticks([density.max(),0],labels=["barcos","mar"],size=45)
    escala.set_label("Density",**{"size":60})
    plt.title("Mapa de Calor das Rotas da Embarcação",**{"size":120},pad=80)
    plt.xlabel("Latitude",labelpad=20,**{"size":60})
    plt.ylabel("Longitude",labelpad=20,**{"size":60})

    # Salva a imagem no disco
    os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)  # Cria o diretório se não existir
    image_path = os.path.join(IMAGE_SAVE_DIR, "heatmap.svg")
    plt.savefig(image_path, format="svg")  # Salva no disco

    # Gera a imagem em memória para resposta HTTP
    img = io.BytesIO()
    plt.savefig(img, format="svg")
    img.seek(0)
    plt.close(fig)

    return Response(img.getvalue(), mimetype="image/svg+xml")