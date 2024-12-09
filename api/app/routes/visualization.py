import os
import matplotlib.pyplot as plt
import io
from flask import Response
from routes.heatmap import get_heatmap_from_csv
from flask import Blueprint, request, Response

# Defina o caminho para salvar as imagens
IMAGE_SAVE_DIR = "img"
visualization_bp = Blueprint("visualization",__name__)

@visualization_bp.route("/", methods=["GET"])
def view_heatmap() -> Response:
    # Gera os dados do heatmap
    data = get_heatmap_from_csv().json
    density = data["density_array"]
    lat_min = data["min_latitude"]
    lat_max = data["max_latitude"]
    lon_min = data["min_longitude"]
    lon_max = data["max_longitude"]

    # Criação do heatmap
    fig = plt.figure(figsize=(10, 8))
    plt.imshow(density, origin="lower", extent=[lat_min, lat_max, lon_min, lon_max], cmap="hot", aspect="auto")
    plt.colorbar(label="Density")
    plt.title("Mapa de Calor das Rotas da Embarcação")
    plt.xlabel("Latitude")
    plt.ylabel("Longitude")

    # Salva a imagem no disco
    os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)  # Cria o diretório se não existir
    image_path = os.path.join(IMAGE_SAVE_DIR, "heatmap.svg")
    plt.savefig(image_path, format="svg")  # Salva no disco

    # Gera a imagem em memória para resposta HTTP
    img = io.BytesIO()
    plt.savefig(img, format="svg")
    img.seek(0)
    plt.close(fig)

    print(f"Imagem salva em: {image_path}")
    return Response(img.getvalue(), mimetype="image/svg+xml")