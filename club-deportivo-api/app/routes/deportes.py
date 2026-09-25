from flask import Blueprint, jsonify
import app.services.deportes_service as deportes_service


deportes_bp = Blueprint("deportes", __name__, url_prefix="/deportes")


@deportes_bp.route("", methods=["GET"])
def get_deportes():
    respuesta, estado = deportes_service.listar_deportes()

    if estado == 204 or not respuesta:
        return "", 204

    return jsonify(respuesta), estado
