from datetime import datetime, timedelta

from app.repositories.reservas_repository import (
    actualizar_estado as actualizar_estado_en_repo,
    crear as crear_en_repo,
    obtener_cancha,
    obtener_con_filtros,
    obtener_por_id as obtener_reserva_por_id,
    obtener_socio,
    verificar_superposicion,
)


ESTADOS_VALIDOS = {"confirmada", "cancelada", "finalizada"}


def respuesta_error(codigo, mensaje, estado):
    return {
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "level": "error",
            }
        ]
    }, estado


def listar_reservas(limit, offset, id_cancha, fecha):
    where_clauses = []
    params = []

    if id_cancha:
        where_clauses.append("id_cancha = %s")
        params.append(id_cancha)

    if fecha:
        where_clauses.append("DATE(fecha_hora_inicio) = %s")
        params.append(fecha)

    where_sql = (
        " WHERE " + " AND ".join(where_clauses)
        if where_clauses
        else ""
    )

    reservas, _total = obtener_con_filtros(
        where_sql,
        params,
        limit,
        offset,
    )

    if not reservas:
        return None, 204

    return {"reservas": reservas}, 200


def obtener_por_id(reserva_id):
    reserva = obtener_reserva_por_id(reserva_id)

    if not reserva:
        return respuesta_error(
            "NOT_FOUND",
            "Reserva no encontrada",
            404,
        )

    return reserva, 200


def crear_reserva(data):
    id_cancha = data.get("id_cancha")
    id_socio = data.get("id_socio")
    fecha = data.get("fecha")
    hora_inicio = data.get("hora_inicio")
    duracion_horas = data.get("duracion_horas", 1)

    if not id_cancha or not id_socio or not fecha or not hora_inicio:
        return respuesta_error(
            "BAD_REQUEST",
            "Campos obligatorios faltantes",
            400,
        )

    if (
        isinstance(duracion_horas, bool)
        or not isinstance(duracion_horas, int)
        or duracion_horas <= 0
    ):
        return respuesta_error(
            "BAD_REQUEST",
            "duracion_horas debe ser un entero positivo",
            400,
        )

    try:
        fecha_hora_inicio = datetime.strptime(
            f"{fecha} {hora_inicio}",
            "%Y-%m-%d %H:%M",
        )
    except ValueError:
        return respuesta_error(
            "BAD_REQUEST",
            "fecha debe tener formato YYYY-MM-DD y hora_inicio HH:MM",
            400,
        )

    fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)

    cancha = obtener_cancha(id_cancha)

    if not cancha:
        return respuesta_error(
            "NOT_FOUND",
            "Cancha no encontrada",
            404,
        )

    if not cancha["activa"]:
        return respuesta_error(
            "BAD_REQUEST",
            "La cancha especificada no está activa",
            400,
        )

    socio = obtener_socio(id_socio)

    if not socio:
        return respuesta_error(
            "NOT_FOUND",
            "Socio no encontrado",
            404,
        )

    if verificar_superposicion(
        id_cancha,
        fecha_hora_inicio,
        fecha_hora_fin,
    ):
        return respuesta_error(
            "CONFLICT",
            "La cancha ya se encuentra reservada en ese horario",
            409,
        )

    tarifa_historica = cancha["precio_hora"]
    precio_total = tarifa_historica * duracion_horas

    reserva_id = crear_en_repo(
        id_cancha,
        id_socio,
        fecha_hora_inicio,
        fecha_hora_fin,
        tarifa_historica,
        precio_total,
    )

    return {
        "id": reserva_id,
        "id_cancha": id_cancha,
        "id_socio": id_socio,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "duracion_horas": duracion_horas,
        "precio_total": precio_total,
    }, 201


def actualizar_estado(reserva_id, nuevo_estado):
    if nuevo_estado not in ESTADOS_VALIDOS:
        return respuesta_error(
            "BAD_REQUEST",
            "El estado debe ser confirmada, cancelada o finalizada",
            400,
        )

    reserva = obtener_reserva_por_id(reserva_id)

    if not reserva:
        return respuesta_error(
            "NOT_FOUND",
            "Reserva no encontrada",
            404,
        )

    actualizar_estado_en_repo(reserva_id, nuevo_estado)

    return {
        "mensaje": "Estado de la reserva actualizado correctamente"
    }, 200
