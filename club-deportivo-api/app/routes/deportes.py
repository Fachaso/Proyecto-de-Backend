from flask import Blueprint, jsonify
from app.services.deportes_service import listar_deportes


deportes_bp = Blueprint("deportes", __name__, url_prefix="/deportes")


@deportes_bp.route("", methods=["GET"])
def get_deportes():
    respuesta, estado = listar_deportes()

    if estado == 204 or not respuesta:
        return "", 204

    return jsonify(respuesta), estado
