from app.repositories.reservas_repository import ReservasRepository

class ReservasService:

    @staticmethod
    def listar_reservas(limit, offset, id_cancha, fecha_hora_inicio):
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

        return reservas, total, extra_params

    @staticmethod
    def obtener_por_id(reserva_id):
        reserva = ReservasRepository.obtener_por_id(reserva_id)
        if not reserva:
            return None
        reserva['fecha'] = str(reserva['fecha'])
        reserva['hora_inicio'] = str(reserva['hora_inicio'])
        return reserva

    @staticmethod
    def crear_reserva(data):
        id_cancha = data.get('id_cancha')
        id_socio = data.get('id_socio')
        fecha = data.get('fecha')
        hora_inicio = data.get('hora_inicio')
        duracion_horas = data.get('duracion_horas', 1)

        if not id_cancha or not id_socio or not fecha or not hora_inicio:
            return {'error': 'Campos obligatorios faltantes'}, 400

        cancha = ReservasRepository.obtener_cancha(id_cancha)
        if not cancha:
            return {'error': 'Cancha no encontrada'}, 404
        if not cancha['activa']:
            return {'error': 'La cancha especificada no está activa'}, 400

        usuario = ReservasRepository.obtener_usuario(id_socio)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        if ReservasRepository.verificar_superposicion(id_cancha, fecha, hora_inicio, duracion_horas):
            return {'error': 'La cancha ya se encuentra reservada en ese horario'}, 409

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
            return {'error': 'Reserva no encontrada'}, 404

        ReservasRepository.actualizar_estado(reserva_id, nuevo_estado)
        return {'message': 'Estado de la reserva actualizado correctamente'}, 200