from flask import Blueprint, jsonify, request
import app.services.socios_service as socios_service
import app.utils.pagination as pagination
from app.validators.common_validators import reject_unknown_query_params
from app.validators.socios_validators import ALLOWED_GET_SOCIOS_PARAMS

socios_bp = Blueprint("socios", __name__, url_prefix="/socios")


@socios_bp.route("", methods=["GET"])
def get_socios():
    """GET /socios (Páginas 4, 6 y 7)."""
    resp = None
    query_args = request.args.to_dict()
    err = reject_unknown_query_params(query_args, ALLOWED_GET_SOCIOS_PARAMS)

    if err:
        resp = jsonify(err), 400
    else:
        limit, offset = pagination.get_pagination_params()
        resultado, status_code = socios_service.listar_socios(query_args, limit, offset)

        if status_code != 200:
            resp = jsonify(resultado), status_code
        else:
            response = pagination.build_pagination_response(
                "socios",
                resultado["socios"],
                resultado["total"],
                limit,
                offset,
                "/socios",
                resultado["extra_params"],
            )
            resp = jsonify(response), 200

    return resp


@socios_bp.route("", methods=["POST"])
def create_socio():
    """
    POST /socios.
    Registra un socio y responde OBLIGATORIAMENTE 201 Created con Location y el JSON creado.
    """
    resp = None
    data = request.get_json(silent=True)
    if data is None:
        data = {}

    resultado, status_code = socios_service.crear_socio(data)

    if status_code == 201:
        headers = {"Location": f"/socios/{resultado['id']}"}
        resp = jsonify(resultado), 201, headers
    else:
        resp = jsonify(resultado), status_code

    return resp


@socios_bp.route("/<int:socio_id>", methods=["GET"])
def get_socio_by_id(socio_id):
    """GET /socios/{id} (Página 6)."""
    resultado, status_code = socios_service.obtener_por_id(socio_id)
    return jsonify(resultado), status_code


@socios_bp.route("/<int:socio_id>", methods=["PATCH"])
def update_socio(socio_id):
    """
    PATCH /socios/{id}.
    Actualiza parcialmente el socio y responde 200 OK con el recurso modificado.
    """
    data = request.get_json(silent=True)
    if data is None:
        data = {}

    resultado, status_code = socios_service.actualizar_socio(socio_id, data)
    return jsonify(resultado), status_code