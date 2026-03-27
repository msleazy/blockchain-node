# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
import os

def create_app():
    app = Flask(__name__)
    CORS(app)  # Permite peticiones entre nodos (cross-origin)
    
    # Configuración de Swagger (OpenAPI)
    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"  # Accede en http://localhost:8001/docs
    }
    
    Swagger(app, config=swagger_config, template={
        "info": {
            "title": f"Blockchain Node API - {os.getenv('NODE_ID', 'nodo')}",
            "description": "Red Blockchain de Grados Académicos",
            "version": "1.0.0"
        },
        "host": f"localhost:{os.getenv('NODE_PORT', '8001')}",
        "basePath": "/"
    })
    
    # Registrar blueprints (rutas)
    from app.routes.chain import chain_bp
    from app.routes.transactions import transactions_bp
    from app.routes.mine import mine_bp
    from app.routes.nodes import nodes_bp
    
    app.register_blueprint(chain_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(mine_bp)
    app.register_blueprint(nodes_bp)
    
    # Ruta de health check
    @app.route("/health")
    def health():
        return {"status": "ok", "node": os.getenv("NODE_ID", "nodo")}, 200
    
    return app