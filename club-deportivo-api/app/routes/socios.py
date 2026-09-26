from flask import Blueprint, request, jsonify
import app.services.socios_service as socios_service
from app.utils.pagination import (get_pagination_params,build_pagination_response,)

socios_bp = Blueprint('socios', __name__, url_prefix='/socios')

@socios_bp.route('', methods=['GET'])
def get_socios():
    limit, offset = get_pagination_params()
    nombre = request.args.get('nombre')
    activo = request.args.get('activo')

    resultado, status_code = socios_service.listar_socios(limit,offset,nombre,activo,)
    if status_code == 204:
        return '', 204

    if status_code != 200:
        return jsonify(resultado), status_code

    response = build_pagination_response("socios",resultado["socios"],resultado["total"],limit,
    offset,"/socios",resultado["extra_params"],)

    return jsonify(response), 200
    
    if status_code == 204:
        return '', 204
        
    return jsonify(resultado), status_code

@socios_bp.route('', methods=['POST'])
def create_socio():
    data = request.get_json() or {}
    resultado, status_code = socios_service.crear_socio(data)

    if status_code == 201:
        headers = {}
        if isinstance(resultado, dict) and 'id' in resultado:
            headers['Location'] = f"/socios/{resultado['id']}"
        return '', 201, headers
        
    return jsonify(resultado), status_code

@socios_bp.route('/<int:socio_id>', methods=['GET'])
def get_socio_by_id(socio_id):
    resultado, status_code = socios_service.obtener_por_id(socio_id)
    return jsonify(resultado), status_code

@socios_bp.route('/<int:socio_id>', methods=['PATCH'])
def update_socio(socio_id):
    data = request.get_json() or {}
    resultado, status_code = socios_service.actualizar_socio(socio_id, data)

    if status_code == 204:
        return '', 204
        
    return jsonify(resultado), status_code
