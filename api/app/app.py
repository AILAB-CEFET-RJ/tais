from flask import Flask
from flask_cors import CORS
from routes.home import home_bp
from routes.routesmap import routesmap_bp
from routes.visualization import visualization_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(home_bp, url_prefix="/")
app.register_blueprint(routesmap_bp, url_prefix="/api")
app.register_blueprint(visualization_bp, url_prefix="/visualization")

if __name__ == '__main__':
    app.run(debug=True)