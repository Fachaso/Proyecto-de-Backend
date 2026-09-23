from app.repositories.reservas_repository import ReservasRepository

class ReservasService:

    @staticmethod
    def listar_reservas(limit, offset, id_cancha, fecha):
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

        reservas, total = ReservasRepository.obtener_con_filtros(where_sql, params, limit, offset)

        for r in reservas:
            r['fecha'] = str(r['fecha'])
            r['hora_inicio'] = str(r['hora_inicio'])

        return {"reservas": reservas}, 200 if reservas else 204

    @staticmethod
    def obtener_por_id(reserva_id):
        reserva = ReservasRepository.obtener_por_id(reserva_id)
        if not reserva:
            return {
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": "Reserva no encontrada",
                        "level": "error"
                    }
                ]
            }, 404

        reserva['fecha'] = str(reserva['fecha'])
        reserva['hora_inicio'] = str(reserva['hora_inicio'])
        return reserva, 200

    @staticmethod
    def crear_reserva(data):
        id_cancha = data.get('id_cancha')
        id_socio = data.get('id_socio')
        fecha = data.get('fecha')
        hora_inicio = data.get('hora_inicio')
        duracion_horas = data.get('duracion_horas', 1)

        # 1. Validar campos requeridos
        if not id_cancha or not id_socio or not fecha or not hora_inicio:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "Campos obligatorios faltantes",
                        "level": "error"
                    }
                ]
            }, 400

        # 2. Validar existencia y estado de la cancha
        cancha = ReservasRepository.obtener_cancha(id_cancha)
        if not cancha:
            return {
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": "Cancha no encontrada",
                        "level": "error"
                    }
                ]
            }, 404

        if not cancha['activa']:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "La cancha especificada no está activa",
                        "level": "error"
                    }
                ]
            }, 400

        # 3. Validar existencia del socio
        socio = ReservasRepository.obtener_usuario(id_socio)
        if not socio:
            return {
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": "Socio no encontrado",
                        "level": "error"
                    }
                ]
            }, 404

        # 4. Validar superposición de horarios en la cancha
        if ReservasRepository.verificar_superposicion(id_cancha, fecha, hora_inicio, duracion_horas):
            return {
                "errors": [
                    {
                        "code": "CONFLICT",
                        "message": "La cancha ya se encuentra reservada en ese horario",
                        "level": "error"
                    }
                ]
            }, 409

        # 5. Guardar la reserva
        precio_total = cancha['precio_hora'] * duracion_horas
        reserva_id = ReservasRepository.crear(id_cancha, id_socio, fecha, hora_inicio, duracion_horas, precio_total)

        return {
            'id': reserva_id,
            'id_cancha': id_cancha,
            'id_socio': id_socio,
            'fecha': str(fecha),
            'hora_inicio': str(hora_inicio),
            'duracion_horas': duracion_horas,
            'precio_total': precio_total
        }, 201

    @staticmethod
    def actualizar_estado(reserva_id, nuevo_estado):
        reserva = ReservasRepository.obtener_por_id(reserva_id)
        if not reserva:
            return {
                "errors": [
                    {
                        "code": "NOT_FOUND",
                        "message": "Reserva no encontrada",
                        "level": "error"
                    }
                ]
            }, 404

        ReservasRepository.actualizar_estado(reserva_id, nuevo_estado)
        return {"mensaje": "Estado de la reserva actualizado correctamente"}, 200