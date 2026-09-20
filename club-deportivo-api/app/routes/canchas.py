from flask import Blueprint, request, jsonify
from app.services.canchas_service import CanchasService
from app.utils.pagination import get_pagination_params, build_pagination_response

canchas_bp = Blueprint('canchas', __name__)

@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    limit, offset = get_pagination_params()
    id_deporte = request.args.get('id_deporte')
    nombre = request.args.get('nombre')
    techada = request.args.get('techada')
    activa = request.args.get('activa')

    canchas, total, extra_params = CanchasService.listar_canchas(limit, offset, id_deporte, nombre, techada, activa)
    response = build_pagination_response('canchas', canchas, total, limit, offset, '/canchas', extra_params)
    return jsonify(response), 200

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def get_cancha_by_id(cancha_id):
    cancha = CanchasService.obtener_por_id(cancha_id)
    if not cancha:
        return jsonify({'error': 'Cancha no encontrada'}), 404
    return jsonify(cancha), 200

@canchas_bp.route('/canchas', methods=['POST'])
def create_cancha():
    data = request.get_json() or {}
    resultado, status_code = CanchasService.crear_cancha(data)
    return jsonify(resultado), status_code

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['PATCH'])
def update_cancha(cancha_id):
    data = request.get_json() or {}
    resultado, status_code = CanchasService.actualizar_cancha(cancha_id, data)
    return jsonify(resultado), status_code

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['DELETE'])
def delete_cancha(cancha_id):
    resultado, status_code = CanchasService.eliminar_cancha(cancha_id)
    if resultado:
        return jsonify(resultado), status_code
    return '', status_code

@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def get_canchas_disponibles():
    fecha = request.args.get('fecha')
    hora_inicio = request.args.get('hora_inicio')
    hora_fin = request.args.get('hora_fin')
    id_deporte = request.args.get('id_deporte')

    if not fecha or not hora_inicio or not hora_fin:
        return jsonify({'error': 'Parámetros fecha, hora_inicio y hora_fin son requeridos'}), 400

    canchas_disponibles = CanchasService.obtener_canchas_disponibles(fecha, hora_inicio, hora_fin, id_deporte)
    return jsonify(canchas_disponibles), 200