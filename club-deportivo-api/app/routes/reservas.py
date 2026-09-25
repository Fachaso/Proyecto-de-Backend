from flask import Blueprint, jsonify, request

from app.services.reservas_service import (
    actualizar_estado,
    crear_reserva,
    listar_reservas,
    obtener_por_id,
)
from app.utils.pagination import get_pagination_params


reservas_bp = Blueprint("reservas", __name__, url_prefix="/reservas")


@reservas_bp.route("", methods=["GET"])
def get_reservas():
    limit, offset = get_pagination_params()
    id_cancha = request.args.get("id_cancha")
    fecha = request.args.get("fecha")

    resultado, status_code = listar_reservas(
        limit,
        offset,
        id_cancha,
        fecha,
    )

    if status_code == 204:
        return "", 204

    return jsonify(resultado), status_code


@reservas_bp.route("/<int:reserva_id>", methods=["GET"])
def get_reserva_by_id(reserva_id):
    resultado, status_code = obtener_por_id(reserva_id)
    return jsonify(resultado), status_code


@reservas_bp.route("", methods=["POST"])
def create_reserva():
    data = request.get_json() or {}
    resultado, status_code = crear_reserva(data)

    if status_code == 201:
        return "", 201, {
            "Location": f"/reservas/{resultado['id']}"
        }

    return jsonify(resultado), status_code


@reservas_bp.route("/<int:reserva_id>/estado", methods=["PUT"])
def update_reserva_estado(reserva_id):
    data = request.get_json() or {}
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return jsonify({
            "errors": [
                {
                    "code": "ERROR_VALIDACION",
                    "message": "El campo 'estado' es obligatorio",
                    "level": "error",
                }
            ]
        }), 400

    resultado, status_code = actualizar_estado(
        reserva_id,
        nuevo_estado,
    )

    return jsonify(resultado), status_code
