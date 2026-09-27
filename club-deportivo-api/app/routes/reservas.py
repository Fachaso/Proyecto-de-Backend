from flask import Blueprint, jsonify, request
import app.services.reservas_service as reservas_service
import app.utils.pagination as pagination
from app.validators.common_validators import reject_unknown_query_params
from app.validators.reservas_validators import ALLOWED_GET_RESERVAS_PARAMS

reservas_bp = Blueprint("reservas", __name__, url_prefix="/reservas")


@reservas_bp.route("", methods=["GET"])
def get_reservas():
    """
    GET /reservas.
    Responde 200 OK con navegación HATEOAS (_links).
    Rechaza parámetros desconocidos con 400 Bad Request.
    """
    resp = None
    query_args = request.args.to_dict()
    err = reject_unknown_query_params(query_args, ALLOWED_GET_RESERVAS_PARAMS)

    if err:
        resp = jsonify(err), 400
    else:
        limit, offset = pagination.get_pagination_params()
        resultado, status_code = reservas_service.listar_reservas(query_args, limit, offset)

        if status_code != 200:
            resp = jsonify(resultado), status_code
        else:
            response = pagination.build_pagination_response(
                "reservas",
                resultado["reservas"],
                resultado["total"],
                limit,
                offset,
                "/reservas",
                resultado["extra_params"],
            )
            resp = jsonify(response), 200

    return resp


@reservas_bp.route("/<int:reserva_id>", methods=["GET"])
def get_reserva_by_id(reserva_id):
    """GET /reservas/{id} (Página 7)."""
    resultado, status_code = reservas_service.obtener_por_id(reserva_id)
    return jsonify(resultado), status_code


@reservas_bp.route("", methods=["POST"])
def create_reserva():
    """
    POST /reservas (Páginas 6 y 7).
    Registra una reserva y responde 201 Created con Location y el JSON creado.
    """
    resp = None
    data = request.get_json(silent=True)
    if data is None:
        data = {}

    resultado, status_code = reservas_service.crear_reserva(data)

    if status_code == 201:
        headers = {"Location": f"/reservas/{resultado['id']}"}
        resp = jsonify(resultado), 201, headers
    else:
        resp = jsonify(resultado), status_code

    return resp


@reservas_bp.route("/<int:reserva_id>/estado", methods=["PUT"])
def update_reserva_estado(reserva_id):
    """
    PUT /reservas/{id}/estado (Páginas 3 y 7).
    Actualiza el estado respetando la máquina de estados e idempotencia.
    """
    data = request.get_json(silent=True)
    if data is None:
        data = {}

    resultado, status_code = reservas_service.actualizar_estado(reserva_id, data)
    return jsonify(resultado), status_code