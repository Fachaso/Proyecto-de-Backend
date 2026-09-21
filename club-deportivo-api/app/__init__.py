from flask import Flask
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

    return app
