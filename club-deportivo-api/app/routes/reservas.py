from flask import Blueprint, jsonify, request

import app.services.reservas_service as reservas_service
import app.utils.pagination as pagination

reservas_bp = Blueprint("reservas", __name__, url_prefix="/reservas")


@reservas_bp.route("", methods=["GET"])
def get_reservas():
    parametros_permitidos = {
        "id_cancha",
        "id_socio",
        "estado",
        "fecha_desde",
        "fecha_hasta",
        "_limit",
        "_offset",
    }

    for parametro in request.args:
        if parametro not in parametros_permitidos:
            return jsonify({
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": (
                            f"Parámetro desconocido: "
                            f"{parametro}"
                        ),
                        "level": "error",
                    }
                ]
            }), 400

    limit, offset, error = (
        pagination.get_pagination_params()
    )

    if error:
        return jsonify({
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": error,
                    "level": "error",
                }
            ]
        }), 400

    id_cancha = request.args.get(
        "id_cancha"
    )

    id_socio = request.args.get(
        "id_socio"
    )

    estado = request.args.get(
        "estado"
    )

    fecha_desde = request.args.get(
        "fecha_desde"
    )

    fecha_hasta = request.args.get(
        "fecha_hasta"
    )

    resultado, status_code = (
        reservas_service.listar_reservas(
            limit,
            offset,
            id_cancha,
            id_socio,
            estado,
            fecha_desde,
            fecha_hasta,
        )
    )

    if status_code == 204:
        return "", 204

    if status_code != 200:
        return jsonify(
            resultado
        ), status_code

    response = (
        pagination.build_pagination_response(
            "reservas",
            resultado["reservas"],
            resultado["total"],
            limit,
            offset,
            "/reservas",
            resultado["extra_params"],
        )
    )

    return jsonify(response), 200


@reservas_bp.route("/<int:reserva_id>", methods=["GET"])
def get_reserva_by_id(reserva_id):
    resultado, status_code = reservas_service.obtener_por_id(reserva_id)
    if status_code == 404:
        return jsonify(resultado), 404
    return jsonify(resultado), status_code


@reservas_bp.route("", methods=["POST"])
def create_reserva():
    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify({
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": (
                        "El cuerpo debe ser "
                        "un objeto JSON"
                    ),
                    "level": "error",
                }
            ]
        }), 400

    resultado, status_code = (
        reservas_service.crear_reserva(
            data
        )
    )

    if status_code == 201:
        headers = {}

        if (
            isinstance(resultado, dict)
            and "id" in resultado
        ):
            headers["Location"] = (
                f"/reservas/{resultado['id']}"
            )

        return "", 201, headers

    return jsonify(
        resultado
    ), status_code

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

    resultado, status_code = reservas_service.actualizar_estado(
        reserva_id,
        nuevo_estado,
    )

    return jsonify(resultado), status_code
