from flask import Blueprint, request, jsonify
from app.services.reservas_service import ReservasService
from app.utils.pagination import get_pagination_params

reservas_bp = Blueprint('reservas', __name__, url_prefix='/reservas')

@reservas_bp.route('', methods=['GET'])
def get_reservas():
    limit, offset = get_pagination_params()
    id_cancha = request.args.get('id_cancha')
    fecha = request.args.get('fecha') or request.args.get('fecha_hora_inicio')

    resultado, status_code = ReservasService.listar_reservas(limit, offset, id_cancha, fecha)

    if status_code == 204:
        return '', 204

    return jsonify(resultado), status_code

@reservas_bp.route('/<int:reserva_id>', methods=['GET'])
def get_reserva_by_id(reserva_id):
    resultado, status_code = ReservasService.obtener_por_id(reserva_id)
    return jsonify(resultado), status_code

@reservas_bp.route('', methods=['POST'])
def create_reserva():
    data = request.get_json() or {}
    resultado, status_code = ReservasService.crear_reserva(data)
    return jsonify(resultado), status_code

@reservas_bp.route('/<int:reserva_id>/estado', methods=['PUT'])
def update_reserva_estado(reserva_id):
    data = request.get_json() or {}
    nuevo_estado = data.get('estado')
    
    if not nuevo_estado:
        return jsonify({
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El campo 'estado' es obligatorio",
                    "level": "error"
                }
            ]
        }), 400

    resultado, status_code = ReservasService.actualizar_estado(reserva_id, nuevo_estado)
    return jsonify(resultado), status_code
