from flask import Blueprint, request, jsonify
from app.db import get_db_connection
from app.utils.pagination import get_pagination_params, build_pagination_response

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/reservas', methods=['GET'])
def get_reservas():
    limit, offset = get_pagination_params()

    id_cancha = request.args.get('id_cancha')
    fecha = request.args.get('fecha')

    where_clauses = []
    params = []
    extra_params = {}

    if id_cancha:
        where_clauses.append("id_cancha = %s")
        params.append(id_cancha)
        extra_params['id_cancha'] = id_cancha

    if fecha:
        where_clauses.append("fecha = %s")
        params.append(fecha)
        extra_params['fecha'] = fecha

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            count_query = f"SELECT COUNT(*) as total FROM reservas{where_sql}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']

            data_query = f"SELECT id, id_cancha, id_usuario, fecha, hora_inicio, duracion_horas, precio_total FROM reservas{where_sql} ORDER BY id ASC LIMIT %s OFFSET %s"
            cursor.execute(data_query, params + [limit, offset])
            reservas = cursor.fetchall()

            for r in reservas:
                r['fecha'] = str(r['fecha'])
                r['hora_inicio'] = str(r['hora_inicio'])

        response = build_pagination_response('reservas', reservas, total, limit, offset, '/reservas', extra_params)
        return jsonify(response), 200
    finally:
        conn.close()

@reservas_bp.route('/reservas/<int:reserva_id>', methods=['GET'])
def get_reserva_by_id(reserva_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, id_cancha, id_usuario, fecha, hora_inicio, duracion_horas, precio_total FROM reservas WHERE id = %s", (reserva_id,))
            reserva = cursor.fetchone()
            if not reserva:
                return jsonify({'error': 'Reserva no encontrada'}), 404

            reserva['fecha'] = str(reserva['fecha'])
            reserva['hora_inicio'] = str(reserva['hora_inicio'])

        return jsonify(reserva), 200
    finally:
        conn.close()

@reservas_bp.route('/reservas', methods=['POST'])
def create_reserva():
    data = request.get_json() or {}
    id_cancha = data.get('id_cancha')
    id_usuario = data.get('id_usuario')
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    duracion_horas = data.get('duracion_horas', 1)

    if not id_cancha or not id_usuario or not fecha or not hora_inicio:
        return jsonify({'error': 'Campos obligatorios faltantes'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, precio_hora, activa FROM canchas WHERE id = %s", (id_cancha,))
            cancha = cursor.fetchone()
            if not cancha:
                return jsonify({'error': 'Cancha no encontrada'}), 404
            if not cancha['activa']:
                return jsonify({'error': 'La cancha especificada no estÃ¡ activa'}), 400

            cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id_usuario,))
            if not cursor.fetchone():
                return jsonify({'error': 'Usuario no encontrado'}), 404

            precio_total = cancha['precio_hora'] * duracion_horas

            cursor.execute(
                "SELECT id FROM reservas WHERE id_cancha = %s AND fecha = %s AND "
                "(hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 3600)) AND ADDTIME(hora_inicio, SEC_TO_TIME(duracion_horas * 3600)) > %s)",
                (id_cancha, fecha, hora_inicio, duracion_horas, hora_inicio)
            )
            if cursor.fetchone():
                return jsonify({'error': 'La cancha ya se encuentra reservada en ese horario'}), 409

            query = "INSERT INTO reservas (id_cancha, id_usuario, fecha, hora_inicio, duracion_horas, precio_total) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (id_cancha, id_usuario, fecha, hora_inicio, duracion_horas, precio_total))
            reserva_id = cursor.lastrowid

        return jsonify({
            'id': reserva_id,
            'id_cancha': id_cancha,
            'id_usuario': id_usuario,
            'fecha': str(fecha),
            'hora_inicio': str(hora_inicio),
            'duracion_horas': duracion_horas,
            'precio_total': precio_total
        }), 201
    finally:
        conn.close()

@reservas_bp.route('/reservas/<int:reserva_id>', methods=['DELETE'])
def delete_reserva(reserva_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM reservas WHERE id = %s", (reserva_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Reserva no encontrada'}), 404

            cursor.execute("DELETE FROM reservas WHERE id = %s", (reserva_id,))
        return '', 204
    finally:
        conn.close()
