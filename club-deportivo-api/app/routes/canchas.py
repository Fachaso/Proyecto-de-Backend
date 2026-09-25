from flask import Blueprint, jsonify, request

import app.services.canchas_service as canchas_service
import app.utils.pagination as pagination


canchas_bp = Blueprint(
    "canchas",
    __name__,
    url_prefix="/canchas",
)


@canchas_bp.route(
    "",
    methods=["GET"],
)
def get_canchas():
    limit, offset = (
        pagination.get_pagination_params()
    )

    id_deporte = request.args.get(
        "id_deporte"
    )

    nombre = request.args.get(
        "nombre"
    )

    techada = request.args.get(
        "techada"
    )

    activa = request.args.get(
        "activa"
    )

    (
        canchas,
        total,
        extra_params,
    ) = canchas_service.listar_canchas(
        limit,
        offset,
        id_deporte,
        nombre,
        techada,
        activa,
    )

    if not canchas:
        return "", 204

    response = (
        pagination
        .build_pagination_response(
            "canchas",
            canchas,
            total,
            limit,
            offset,
            "/canchas",
            extra_params,
        )
    )

    return jsonify(response), 200


@canchas_bp.route(
    "/disponibles",
    methods=["GET"],
)
def get_canchas_disponibles():
    limit, offset = (
        pagination.get_pagination_params()
    )

    fecha = request.args.get(
        "fecha"
    )

    hora_inicio = request.args.get(
        "hora_inicio"
    )

    hora_fin = request.args.get(
        "hora_fin"
    )

    id_deporte = request.args.get(
        "id_deporte"
    )

    techada = request.args.get(
        "techada"
    )

    if (
        not fecha
        or not hora_inicio
        or not hora_fin
    ):
        return jsonify(
            {
                "errors": [
                    {
                        "code": "ERROR_VALIDACION",
                        "message": "Parámetros fecha, hora_inicio y hora_fin son requeridos",
                        "level": "error",
                        "description": "Debe proporcionar fecha, hora_inicio y hora_fin para consultar disponibilidad",
                    }
                ]
            }
        ), 400

    resultado, status_code = (
        canchas_service
        .obtener_canchas_disponibles(
            fecha,
            hora_inicio,
            hora_fin,
            id_deporte,
            techada,
            limit,
            offset,
        )
    )

    if status_code != 200:
        return jsonify(
            resultado
        ), status_code

    response = (
        pagination
        .build_pagination_response(
            "canchas",
            resultado["canchas"],
            resultado["total"],
            limit,
            offset,
            "/canchas/disponibles",
            resultado["extra_params"],
        )
    )

    return jsonify(response), 200


@canchas_bp.route(
    "/<int:cancha_id>",
    methods=["GET"],
)
def get_cancha_by_id(cancha_id):
    cancha = (
        canchas_service.obtener_por_id(
            cancha_id
        )
    )

    if not cancha:
        return jsonify(
            {
                "errors": [
                    {
                        "code": "RECURSO_NO_ENCONTRADO",
                        "message": "Cancha no encontrada",
                        "level": "error",
                        "description": f"No existe una cancha con el id {cancha_id}",
                    }
                ]
            }
        ), 404

    return jsonify(cancha), 200


@canchas_bp.route(
    "",
    methods=["POST"],
)
def create_cancha():
    data = request.get_json(
        silent=True
    )

    if data is None:
        data = {}

    resultado, status_code = (
        canchas_service.crear_cancha(
            data
        )
    )

    if status_code == 201:
        headers = {}

        if (
            isinstance(
                resultado,
                dict,
            )
            and "id" in resultado
        ):
            headers[
                "Location"
            ] = (
                f"/canchas/"
                f"{resultado['id']}"
            )

        return "", 201, headers

    return jsonify(
        resultado
    ), status_code


@canchas_bp.route(
    "/<int:cancha_id>",
    methods=["PATCH"],
)
def update_cancha(cancha_id):
    data = request.get_json(
        silent=True
    )

    if data is None:
        data = {}

    resultado, status_code = (
        canchas_service
        .actualizar_cancha(
            cancha_id,
            data,
        )
    )

    return jsonify(
        resultado
    ), status_code


@canchas_bp.route(
    "/<int:cancha_id>",
    methods=["DELETE"],
)
def delete_cancha(cancha_id):
    resultado, status_code = (
        canchas_service
        .eliminar_cancha(
            cancha_id
        )
    )

    if status_code == 204:
        return "", 204

    return jsonify(
        resultado
    ), status_code