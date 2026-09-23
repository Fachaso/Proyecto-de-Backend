from flask import Blueprint, request, jsonify
from app.services.socios_service import SociosService
from app.utils.pagination import get_pagination_params

socios_bp = Blueprint('socios', __name__, url_prefix='/socios')

@socios_bp.route('', methods=['GET'])
def get_socios():
    limit, offset = get_pagination_params()
    nombre = request.args.get('nombre')
    email = request.args.get('email')
    activo = request.args.get('activo')

    resultado, status_code = SociosService.listar_socios(limit, offset, nombre, email, activo)
    
    if status_code == 204:
        return '', 204
        
    return jsonify(resultado), status_code

@socios_bp.route('', methods=['POST'])
def create_socio():
    data = request.get_json() or {}
    resultado, status_code = SociosService.crear_socio(data)
    return jsonify(resultado), status_code

@socios_bp.route('/<int:socio_id>', methods=['GET'])
def get_socio_by_id(socio_id):
    resultado, status_code = SociosService.obtener_por_id(socio_id)
    return jsonify(resultado), status_code

@socios_bp.route('/<int:socio_id>', methods=['PATCH'])
def update_socio(socio_id):
    data = request.get_json() or {}
    resultado, status_code = SociosService.actualizar_socio(socio_id, data)
    return jsonify(resultado), status_code