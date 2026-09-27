from flask import Blueprint, jsonify, request
import app.services.canchas_service as canchas_service
import app.utils.pagination as pagination
from app.validators.common_validators import reject_unknown_query_params
from app.validators.canchas_validators import (
    ALLOWED_GET_CANCHAS_PARAMS,
    ALLOWED_GET_DISPONIBLES_PARAMS
)

canchas_bp = Blueprint("canchas", __name__, url_prefix="/canchas")


@canchas_bp.route("", methods=["GET"])
def get_canchas():
    resp = None
    query_args = request.args.to_dict()
    err = reject_unknown_query_params(query_args, ALLOWED_GET_CANCHAS_PARAMS)

    if err:
        resp = jsonify(err), 400
    else:
        limit, offset = pagination.get_pagination_params()
        resultado, status_code = canchas_service.listar_canchas(query_args, limit, offset)

        if status_code != 200:
            resp = jsonify(resultado), status_code
        else:
            response = pagination.build_pagination_response(
                "canchas",
                resultado["canchas"],
                resultado["total"],
                limit,
                offset,
                "/canchas",
                resultado["extra_params"],
            )
            resp = jsonify(response), 200

    return resp


@canchas_bp.route("/disponibles", methods=["GET"])
def get_canchas_disponibles():
    resp = None
    query_args = request.args.to_dict()
    err = reject_unknown_query_params(query_args, ALLOWED_GET_DISPONIBLES_PARAMS)

    if err:
        resp = jsonify(err), 400
    else:
        limit, offset = pagination.get_pagination_params()
        resultado, status_code = canchas_service.obtener_canchas_disponibles(query_args, limit, offset)

        if status_code != 200:
            resp = jsonify(resultado), status_code
        else:
            response = pagination.build_pagination_response(
                "canchas",
                resultado["canchas"],
                resultado["total"],
                limit,
                offset,
                "/canchas/disponibles",
                resultado["extra_params"],
            )
            resp = jsonify(response), 200

    return resp


@canchas_bp.route("/<int:cancha_id>", methods=["GET"])
def get_cancha_by_id(cancha_id):
    resp = None
    cancha = canchas_service.obtener_por_id(cancha_id)

    if not cancha:
        resp = jsonify({
            "errors": [{
                "code": "NOT_FOUND",
                "message": "Cancha no encontrada",
                "level": "error",
                "description": f"No existe una cancha con el id {cancha_id}"
            }]
        }), 404
    else:
        resp = jsonify(cancha), 200

    return resp


@canchas_bp.route("", methods=["POST"])
def create_cancha():
    resp = None
    data = request.get_json(silent=True)
    if data is None:
        data = {}

    resultado, status_code = canchas_service.crear_cancha(data)

    if status_code == 201:
        headers = {"Location": f"/canchas/{resultado['id']}"}
        resp = jsonify(resultado), 201, headers
    else:
        resp = jsonify(resultado), status_code

    return resp


@canchas_bp.route("/<int:cancha_id>", methods=["PATCH"])
def update_cancha(cancha_id):
    data = request.get_json(silent=True)
    if data is None:
        data = {}

    resultado, status_code = canchas_service.actualizar_cancha(cancha_id, data)
    return jsonify(resultado), status_code


@canchas_bp.route("/<int:cancha_id>", methods=["DELETE"])
def delete_cancha(cancha_id):
    resp = None
    resultado, status_code = canchas_service.eliminar_cancha(cancha_id)

    if status_code == 204:
        resp = "", 204
    else:
        resp = jsonify(resultado), status_code

    return resp