import os
import matplotlib
matplotlib.use("Agg")  # Define o backend para uso não interativo
import matplotlib.pyplot as plt
import io
from flask import Response
from routes.routesmap import get_routesmap_from_csv
from flask import Blueprint, request, Response
from mpl_toolkits.basemap import Basemap
import numpy as np
from random import random
import colorsys

# Defina o caminho para salvar as imagens
IMAGE_SAVE_DIR = "img"
visualization_bp = Blueprint("visualization", __name__)

@visualization_bp.route("/", methods=["GET"])
def view_routesmap() -> Response:
    # Gera os dados do routesmap
    data = get_routesmap_from_csv().json
    coordinates = list((tuple(c) for c in data["coordinates"]))
    if coordinates is None or len(coordinates) == 0:
        return Response("Erro: Dados de densidade não estão disponíveis.", status=400)
    
    routes = {}

    for line in coordinates:
        if list(routes.keys()).count(line[2])==1:
            routes[line[2]].append((line[0],line[1]))
        else:
            routes[line[2]]=[(line[0],line[1])]
    # from flask import jsonify
    # return jsonify(routes)

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
        lat_padding, lon_padding = 0, 0
        
    else:
        # Calcular padding adequado (ajustado)
        if abs((lat_max - lat_min))>abs((lon_max - lon_min)):
                lat_padding = max((lat_max - lat_min),0)/4
                lon_padding = lat_padding
        else:
            lon_padding = max((lon_max - lon_min),0)/4
            lat_padding = lon_padding

    # Criação do routesmap
    fig = plt.figure(figsize=(10, 10))
    try:
        # criando recorte contendo rota encontrada, com no mínimo 9 graus em latitude e longitude, do mapa mundi usando projeção cilindrica de Miller
        mapamundi = Basemap(
            projection="mill",
            llcrnrlat=lat_min - lat_padding,
            llcrnrlon=lon_min - lon_padding,
            urcrnrlat=lat_max + lat_padding,
            urcrnrlon=lon_max + lon_padding,
            resolution='f'
        )
        mapamundi.drawcoastlines(linewidth=1)
        mapamundi.drawcountries(linewidth=3)
        mapamundi.drawstates(linestyle="dashed")
        mapamundi.fillcontinents(color='lightgreen', lake_color='blue')
        mapamundi.drawmapboundary(fill_color="blue")

        # Sobrepor scatterplot de cada embarcação ao mapa
        for id, coords in routes.items():
            # 0.5 a 0.7 é hue de azul
            color = [random(),random(),random()]
            while color[0] >= 0.5 and color[0] < 0.7:
                color[0]=random()
            while color[1] < 0.7:
                color[1]=random()
            while color[2] < 0.5:
                color[2]=random()
            color = colorsys.hsv_to_rgb(*color)
            lats, lons = zip(*coords)
            x, y = mapamundi(lons, lats)
            mapamundi.plot(x,y,color=color, marker=None,zorder=5,lw=1)

        plt.title("Mapa de Calor das Rotas da Embarcação", fontsize=24)
        plt.xlabel("Longitude", fontsize=20)
        plt.ylabel("Latitude", fontsize=20)

        os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
        image_path = os.path.join(IMAGE_SAVE_DIR, "routes.svg")
        plt.savefig(image_path, format="svg")

        # Gera a imagem em memória para resposta HTTP
        img = io.BytesIO()
        plt.savefig(img, format="svg")
        img.seek(0)
    finally:
        plt.close(fig)  # Garante que o recurso será liberado

    return Response(img.getvalue(), mimetype="image/svg+xml")
