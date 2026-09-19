from app.repositories.canchas_repository import CanchasRepository

class CanchasService:

    @staticmethod
    def listar_canchas(limit, offset, id_deporte, nombre, techada, activa):
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

        canchas, total = CanchasRepository.obtener_con_filtros(where_sql, params, limit, offset)

        for c in canchas:
            c['techada'] = bool(c['techada'])
            c['activa'] = bool(c['activa'])

        return canchas, total, extra_params

    @staticmethod
    def obtener_por_id(cancha_id):
        cancha = CanchasRepository.obtener_por_id(cancha_id)
        if not cancha:
            return None
        cancha['techada'] = bool(cancha['techada'])
        cancha['activa'] = bool(cancha['activa'])
        return cancha

    @staticmethod
    def crear_cancha(data):
        nombre = str(data.get('nombre', '')).strip()
        id_deporte = data.get('id_deporte')
        precio_hora = data.get('precio_hora')
        techada = bool(data.get('techada', False))
        activa = bool(data.get('activa', True))

        if not nombre or not id_deporte or precio_hora is None:
            return {'error': 'Campos obligatorios faltantes'}, 400

        if not isinstance(precio_hora, int) or precio_hora <= 0:
            return {'error': 'El precio_hora debe ser un entero positivo'}, 400

        if not CanchasRepository.verificar_deporte(id_deporte):
            return {'error': 'Deporte no encontrado'}, 400

        cancha_id = CanchasRepository.crear(id_deporte, nombre, precio_hora, techada, activa)

        return {
            'id': cancha_id,
            'id_deporte': id_deporte,
            'nombre': nombre,
            'precio_hora': precio_hora,
            'techada': techada,
            'activa': activa
        }, 201

    @staticmethod
    def actualizar_cancha(cancha_id, data):
        cancha_actual = CanchasRepository.obtener_por_id(cancha_id)
        if not cancha_actual:
            return {'error': 'Cancha no encontrada'}, 404

        fields = []
        params = []

        if 'nombre' in data:
            nombre = str(data['nombre']).strip()
            if not nombre:
                return {'error': 'El nombre no puede estar vacío'}, 400
            fields.append("nombre = %s")
            params.append(nombre)

        if 'id_deporte' in data:
            id_deporte = data['id_deporte']
            if not CanchasRepository.verificar_deporte(id_deporte):
                return {'error': 'Deporte no encontrado'}, 400
            fields.append("id_deporte = %s")
            params.append(id_deporte)

        if 'precio_hora' in data:
            precio_hora = data['precio_hora']
            if not isinstance(precio_hora, int) or precio_hora <= 0:
                return {'error': 'El precio_hora debe ser un entero positivo'}, 400
            fields.append("precio_hora = %s")
            params.append(precio_hora)

        if 'techada' in data:
            fields.append("techada = %s")
            params.append(bool(data['techada']))

        if 'activa' in data:
            fields.append("activa = %s")
            params.append(bool(data['activa']))

        if not fields:
            return {'error': 'No hay campos para actualizar'}, 400

        CanchasRepository.actualizar(cancha_id, fields, params)
        return CanchasService.obtener_por_id(cancha_id), 200

    @staticmethod
    def eliminar_cancha(cancha_id):
        if not CanchasRepository.obtener_por_id(cancha_id):
            return {'error': 'Cancha no encontrada'}, 404

        if CanchasRepository.verificar_reservas_asociadas(cancha_id):
            return {'error': 'No se puede eliminar una cancha con reservas asociadas'}, 409

        CanchasRepository.eliminar(cancha_id)
        return None, 204