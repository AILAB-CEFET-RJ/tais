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
    if density is None or density.size == 0:
        return Response("Erro: Dados de densidade não estão disponíveis.", status=400)

    # Verificar limites
    lat_min = data["min_latitude"]
    lat_max = data["max_latitude"]
    lon_min = data["min_longitude"]
    lon_max = data["max_longitude"]

    # Obter parâmetros bbox opcionais
    bbox = request.args.get("bbox")
    if bbox:
        print("Recebido bbox:", bbox)
        try:
            bbox = list(map(float, bbox.split(',')))
            assert len(bbox) == 4, "Bounding box deve conter exatamente 4 valores (lat_min, lon_min, lat_max, lon_max)"
            lat_min, lon_min, lat_max, lon_max = bbox

            if not (-90 <= lat_min <= 90 and -90 <= lat_max <= 90):
                raise ValueError("As coordenadas de latitude devem estar no intervalo de -90 a 90.")
            if not (-180 <= lon_min <= 180 and -180 <= lon_max <= 180):
                raise ValueError("As coordenadas de longitude devem estar no intervalo de -180 a 180.")
            assert lat_min < lat_max and lon_min < lon_max, "Coordenadas da bounding box inválidas"
        except (ValueError, AssertionError) as e:
            return Response(f"Erro no formato da bounding box: {str(e)}", status=400)

    print(f"Lat_Min: {lat_min}, Lon_Min: {lon_min}, Lat_Max: {lat_max}, Lon_Max: {lon_max}")

    # Calcular padding adequado (ajustado)
    lat_padding = max(0.5 - (lat_max - lat_min), 0) / 2
    lon_padding = max(0.5 - (lon_max - lon_min), 0) / 2

    # Criação do heatmap
    fig = plt.figure(figsize=(10, 10))
    # criando recorte contendo rota encontrada, com no mínimo 40 graus em latitude e longitude, do mapa mundi usando projeção cilindrica de Miller
    mapamundi = Basemap(
        projection="mill",
        llcrnrlat=lat_min - lat_padding,
        llcrnrlon=lon_min - lon_padding,
        urcrnrlat=lat_max + lat_padding,
        urcrnrlon=lon_max + lon_padding,
        resolution='i'
    )
    mapamundi.drawcoastlines(linewidth=1)
    mapamundi.drawcountries(linewidth=1)
    mapamundi.drawstates(linestyle="dashed")

    # Gerar coordenadas para o heatmap
    lons = np.linspace(lon_min, lon_max, density.shape[1])
    lats = np.linspace(lat_min, lat_max, density.shape[0])
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Sobrepor heatmap ao mapa
    heatmap = mapamundi.pcolormesh(lon_grid, lat_grid, density, cmap='bwr', shading='auto', latlon=True)

    mapamundi.fillcontinents(color='lightgreen', lake_color='blue')
    mapamundi.drawmapboundary(fill_color="blue")


    # plt.imshow(density, origin="lower", extent=[lat_min, lat_max, lon_min, lon_max], cmap="hot", aspect="auto")
    # escala = plt.colorbar(heatmap)
    # escala.set_ticks([density.max(),0],labels=["barcos","mar"],size=45)
    # escala.set_label("Density",**{"size":60})
    # plt.title("Mapa de Calor das Rotas da Embarcação",**{"size":120},pad=80)
    # plt.xlabel("Latitude",labelpad=20,**{"size":60})
    # plt.ylabel("Longitude",labelpad=20,**{"size":60})

    escala = plt.colorbar(heatmap)
    escala.set_label("Density", fontsize=20)
    escala.set_ticks([density.max(),0],labels=["barcos","mar"],size=20)
    plt.title("Mapa de Calor das Rotas da Embarcação", fontsize=24)
    plt.xlabel("Longitude", fontsize=20)
    plt.ylabel("Latitude", fontsize=20)

    os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
    image_path = os.path.join(IMAGE_SAVE_DIR, "heatmap.svg")
    plt.savefig(image_path, format="svg")

    # Gera a imagem em memória para resposta HTTP
    img = io.BytesIO()
    plt.savefig(img, format="svg")
    img.seek(0)
    plt.close(fig)

    return Response(img.getvalue(), mimetype="image/svg+xml")
