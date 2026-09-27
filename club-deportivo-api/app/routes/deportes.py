from flask import Blueprint, jsonify, request
import app.services.deportes_service as deportes_service
from app.validators.common_validators import reject_unknown_query_params

deportes_bp = Blueprint("deportes", __name__, url_prefix="/deportes")


@deportes_bp.route("", methods=["GET"])
def get_deportes():
    """
    GET /deportes.
    Devuelve la lista de deportes precargados con 200 OK.
    No requiere paginación.
    Rechaza cualquier query param con 400 Bad Request (set vacío de permitidos).
    """
    resp = None
    query_args = request.args.to_dict()
    
    # El enunciado no contempla ningún query param para /deportes
    err = reject_unknown_query_params(query_args, allowed_params=set())

    if err:
        resp = jsonify(err), 400
    else:
        deportes, status = deportes_service.listar_deportes()
        resp = jsonify(deportes), status

    return resp