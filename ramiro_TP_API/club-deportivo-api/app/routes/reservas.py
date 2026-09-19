from flask import Blueprint, request, jsonify
from app.services.reservas_service import ReservasService
from app.utils.pagination import get_pagination_params, build_pagination_response

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/reservas', methods=['GET'])
def get_reservas():
    limit, offset = get_pagination_params()
    id_cancha = request.args.get('id_cancha')
    fecha = request.args.get('fecha')

    reservas, total, extra_params = ReservasService.listar_reservas(limit, offset, id_cancha, fecha)
    response = build_pagination_response('reservas', reservas, total, limit, offset, '/reservas', extra_params)
    return jsonify(response), 200

@reservas_bp.route('/reservas/<int:reserva_id>', methods=['GET'])
def get_reserva_by_id(reserva_id):
    reserva = ReservasService.obtener_por_id(reserva_id)
    if not reserva:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    return jsonify(reserva), 200

@reservas_bp.route('/reservas', methods=['POST'])
def create_reserva():
    data = request.get_json() or {}
    resultado, status_code = ReservasService.crear_reserva(data)
    return jsonify(resultado), status_code

@reservas_bp.route('/reservas/<int:reserva_id>', methods=['DELETE'])
def delete_reserva(reserva_id):
    exito = ReservasService.eliminar_reserva(reserva_id)
    if not exito:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    return '', 204