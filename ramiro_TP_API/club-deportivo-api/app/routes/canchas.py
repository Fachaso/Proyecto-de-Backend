from flask import Blueprint, request, jsonify
from app.db import get_db_connection
from app.utils.pagination import get_pagination_params, build_pagination_response

canchas_bp = Blueprint('canchas', __name__)

@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    limit, offset = get_pagination_params()

    id_deporte = request.args.get('id_deporte')
    nombre = request.args.get('nombre')
    techada = request.args.get('techada')
    activa = request.args.get('activa')

    where_clauses = []
    params = []
    extra_params = {}

    if id_deporte:
        where_clauses.append("id_deporte = %s")
        params.append(id_deporte)
        extra_params['id_deporte'] = id_deporte

    if nombre:
        where_clauses.append("LOWER(nombre) LIKE %s")
        params.append(f"%{nombre.lower()}%")
        extra_params['nombre'] = nombre

    if techada in ['true', 'false']:
        where_clauses.append("techada = %s")
        params.append(1 if techada == 'true' else 0)
        extra_params['techada'] = techada

    if activa in ['true', 'false']:
        where_clauses.append("activa = %s")
        params.append(1 if activa == 'true' else 0)
        extra_params['activa'] = activa

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            count_query = f"SELECT COUNT(*) as total FROM canchas{where_sql}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']

            data_query = f"SELECT id, id_deporte, nombre, precio_hora, techada, activa FROM canchas{where_sql} ORDER BY id ASC LIMIT %s OFFSET %s"
            cursor.execute(data_query, params + [limit, offset])
            canchas = cursor.fetchall()

            for c in canchas:
                c['techada'] = bool(c['techada'])
                c['activa'] = bool(c['activa'])

        response = build_pagination_response('canchas', canchas, total, limit, offset, '/canchas', extra_params)
        return jsonify(response), 200
    finally:
        conn.close()

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def get_cancha_by_id(cancha_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, id_deporte, nombre, precio_hora, techada, activa FROM canchas WHERE id = %s", (cancha_id,))
            cancha = cursor.fetchone()
            if not cancha:
                return jsonify({'error': 'Cancha no encontrada'}), 404
            cancha['techada'] = bool(cancha['techada'])
            cancha['activa'] = bool(cancha['activa'])
        return jsonify(cancha), 200
    finally:
        conn.close()

@canchas_bp.route('/canchas', methods=['POST'])
def create_cancha():
    data = request.get_json() or {}
    nombre = str(data.get('nombre', '')).strip()
    id_deporte = data.get('id_deporte')
    precio_hora = data.get('precio_hora')
    techada = bool(data.get('techada', False))
    activa = bool(data.get('activa', True))

    if not nombre or not id_deporte or precio_hora is None:
        return jsonify({'error': 'Campos obligatorios faltantes'}), 400

    if not isinstance(precio_hora, int) or precio_hora <= 0:
        return jsonify({'error': 'El precio_hora debe ser un entero positivo'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM deportes WHERE id = %s", (id_deporte,))
            if not cursor.fetchone():
                return jsonify({'error': 'Deporte no encontrado'}), 400

            query = "INSERT INTO canchas (id_deporte, nombre, precio_hora, techada, activa) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (id_deporte, nombre, precio_hora, techada, activa))
            cancha_id = cursor.lastrowid

        return jsonify({
            'id': cancha_id,
            'id_deporte': id_deporte,
            'nombre': nombre,
            'precio_hora': precio_hora,
            'techada': techada,
            'activa': activa
        }), 201
    finally:
        conn.close()

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['PATCH'])
def update_cancha(cancha_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM canchas WHERE id = %s", (cancha_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Cancha no encontrada'}), 404

            fields = []
            params = []

            if 'nombre' in data:
                nombre = str(data['nombre']).strip()
                if not nombre:
                    return jsonify({'error': 'El nombre no puede estar vacÃo'}), 400
                fields.append("nombre = %s")
                params.append(nombre)

            if 'id_deporte' in data:
                id_deporte = data['id_deporte']
                cursor.execute("SELECT id FROM deportes WHERE id = %s", (id_deporte,))
                if not cursor.fetchone():
                    return jsonify({'error': 'Deporte no encontrado'}), 400
                fields.append("id_deporte = %s")
                params.append(id_deporte)

            if 'precio_hora' in data:
                precio_hora = data['precio_hora']
                if not isinstance(precio_hora, int) or precio_hora <= 0:
                    return jsonify({'error': 'El precio_hora debe ser un entero positivo'}), 400
                fields.append("precio_hora = %s")
                params.append(precio_hora)

            if 'techada' in data:
                fields.append("techada = %s")
                params.append(bool(data['techada']))

            if 'activa' in data:
                fields.append("activa = %s")
                params.append(bool(data['activa']))

            if not fields:
                return jsonify({'error': 'No hay campos para actualizar'}), 400

            params.append(cancha_id)
            cursor.execute(f"UPDATE canchas SET {', '.join(fields)} WHERE id = %s", params)

            cursor.execute("SELECT id, id_deporte, nombre, precio_hora, techada, activa FROM canchas WHERE id = %s", (cancha_id,))
            updated_cancha = cursor.fetchone()
            updated_cancha['techada'] = bool(updated_cancha['techada'])
            updated_cancha['activa'] = bool(updated_cancha['activa'])

        return jsonify(updated_cancha), 200
    finally:
        conn.close()

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['DELETE'])
def delete_cancha(cancha_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM canchas WHERE id = %s", (cancha_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Cancha no encontrada'}), 404

            cursor.execute("SELECT id FROM reservas WHERE id_cancha = %s LIMIT 1", (cancha_id,))
            if cursor.fetchone():
                return jsonify({'error': 'No se puede eliminar una cancha con reservas asociadas'}), 409

            cursor.execute("DELETE FROM canchas WHERE id = %s", (cancha_id,))
        return '', 204
    finally:
        conn.close()
