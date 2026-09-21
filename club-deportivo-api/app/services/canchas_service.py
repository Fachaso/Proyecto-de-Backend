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
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "Campos obligatorios faltantes",
                        "level": "error"
                    }
                ]
            }, 400

        if not isinstance(precio_hora, int) or precio_hora <= 0:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "El precio_hora debe ser un entero positivo",
                        "level": "error"
                    }
                ]
            }, 400

        if not CanchasRepository.verificar_deporte(id_deporte):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "Deporte no encontrado",
                        "level": "error"
                    }
                ]
            }, 400

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
            return {
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": "Cancha no encontrada",
                        "level": "error"
                    }
                ]
            }, 404

        fields = []
        params = []

        if 'nombre' in data:
            nombre = str(data['nombre']).strip()
            if not nombre:
                return {
                    "errors": [
                        {
                            "code": "BAD_REQUEST",
                            "message": "El nombre no puede estar vacío",
                            "level": "error"
                        }
                    ]
                }, 400
            fields.append("nombre = %s")
            params.append(nombre)

        if 'id_deporte' in data:
            id_deporte = data['id_deporte']
            if not CanchasRepository.verificar_deporte(id_deporte):
                return {
                    "errors": [
                        {
                            "code": "BAD_REQUEST",
                            "message": "Deporte no encontrado",
                            "level": "error"
                        }
                    ]
                }, 400
                
            fields.append("id_deporte = %s")
            params.append(id_deporte)

        if 'precio_hora' in data:
            precio_hora = data['precio_hora']
            if not isinstance(precio_hora, int) or precio_hora <= 0:
                return {
                    "errors": [
                        {
                            "code": "BAD_REQUEST",
                            "message": "El precio_hora debe ser un entero positivo",
                            "level": "error"
                        }
                    ]
                }, 400

            fields.append("precio_hora = %s")
            params.append(precio_hora)

        if 'techada' in data:
            fields.append("techada = %s")
            params.append(bool(data['techada']))

        if 'activa' in data:
            fields.append("activa = %s")
            params.append(bool(data['activa']))

        if not fields:
            return {
                    "errors": [
                        {
                            "code": "BAD_REQUEST",
                            "message": "No hay campos para actualizar",
                            "level": "error"
                        }
                    ]
                }, 400

        CanchasRepository.actualizar(cancha_id, fields, params)
        return CanchasService.obtener_por_id(cancha_id), 200

    @staticmethod
    def eliminar_cancha(cancha_id):
        if not CanchasRepository.obtener_por_id(cancha_id):
            return {
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": "Cancha no encontrada",
                        "level": "error"
                    }
                ]
            }, 404

        if CanchasRepository.verificar_reservas_asociadas(cancha_id):
            return {
                "errors": [
                    {
                        "code": "CONFLICT",
                        "message": "No se puede eliminar una cancha con reservas asociadas",
                        "level": "error"
                    }
                ]
            }, 409

        CanchasRepository.eliminar(cancha_id)
        return None, 204

    @staticmethod
    def obtener_canchas_disponibles(fecha, hora_inicio, hora_fin, id_deporte):
        if not CanchasRepository.verificar_formato_fecha(fecha):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "Formato de fecha inválido. Se espera YYYY-MM-DD",
                        "level": "error"
                    }
                ]
            }, 400

        if not CanchasRepository.verificar_formato_hora(hora_inicio) or not CanchasRepository.verificar_formato_hora(hora_fin):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "Formato de hora inválido. Se espera HH:MM",
                        "level": "error"
                    }
                ]
            }, 400

        if hora_inicio >= hora_fin:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "La hora de inicio debe ser menor que la hora de fin",
                        "level": "error"
                    }
                ]
            }, 400

        canchas_disponibles = CanchasRepository.obtener_canchas_disponibles(fecha, hora_inicio, hora_fin, id_deporte)
        for c in canchas_disponibles:
            c['techada'] = bool(c['techada'])
            c['activa'] = bool(c['activa'])

        return canchas_disponibles