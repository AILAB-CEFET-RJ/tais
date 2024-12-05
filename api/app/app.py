from flask import Flask
from flask_cors import CORS
from routes.home import home_bp
from routes.heatmap import heatmap_bp
from routes.vessel import vessel_bp
from routes.visualization import visualization_bp

app = Flask(__name__)
CORS(app)

#! definicao das rotas
app.register_blueprint(home_bp, url_prefix="/")
app.register_blueprint(heatmap_bp, url_prefix="/api")
app.register_blueprint(vessel_bp, url_prefix="/vessel")
app.register_blueprint(visualization_bp, url_prefix="/visualization")

if __name__ == '__main__':
    app.run(debug=True)