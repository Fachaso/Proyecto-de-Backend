from flask import Flask, jsonify
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)

    from app.routes.deportes import deportes_bp
    from app.routes.canchas import canchas_bp
    from app.routes.reservas import reservas_bp
    from app.routes.socios import socios_bp

    app.register_blueprint(deportes_bp)
    app.register_blueprint(canchas_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(socios_bp)
    @app.errorhandler(500)
    def manejar_error_interno(error):
        return jsonify({
            "errors": [
                {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Error interno del servidor",
                    "level": "error",
                }
            ]
        }), 500
    return app
