from flask import Blueprint, request, jsonify
from app.services.socios_service import SociosService
from app.utils.pagination import get_pagination_params, build_pagination_response

socios_bp = Blueprint('socios', __name__)

@socios_bp.route('/socios', methods=['GET'])
def get_socios():
    limit, offset = get_pagination_params()
    nombre = request.args.get('nombre')
    email = request.args.get('email')
    activo = request.args.get('activo')

    socios, total, extra_params = SociosService.listar_socios(limit, offset, nombre, email, activo)
    response = build_pagination_response('socios', socios, total, limit, offset, '/socios', extra_params)
    return jsonify(response), 200

@socios_bp.route('/socios', methods=['POST'])
def create_socio():
    data = request.get_json() or {}
    resultado, status_code = SociosService.crear_socio(data)
    return jsonify(resultado), status_code

@socios_bp.route('/socios/<int:socio_id>', methods=['GET'])
def get_socio_by_id(socio_id):
    socio = SociosService.obtener_por_id(socio_id)
    if not socio:
        return jsonify({'error': 'Socio no encontrado'}), 404
    return jsonify(socio), 200

@socios_bp.route('/socios/<int:socio_id>', methods=['PATCH'])
def update_socio(socio_id):
    data = request.get_json() or {}
    resultado, status_code = SociosService.actualizar_socio(socio_id, data)
    return jsonify(resultado), status_code