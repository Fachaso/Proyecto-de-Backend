from datetime import datetime, time, timezone, timedelta

from app.repositories.reservas_repository import (
    actualizar_estado as actualizar_estado_en_repo,
    crear as crear_en_repo,
    obtener_cancha,
    obtener_con_filtros,
    obtener_por_id as obtener_reserva_por_id,
    obtener_socio,
    verificar_superposicion_cancha,
    verificar_superposicion_socio,
)

TZ_ARG = timezone(timedelta(hours=-3))
HORA_APERTURA = time(8, 0)
HORA_CIERRE = time(23, 0)


def respuesta_error(codigo, mensaje, estado_http):
    return {
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "level": "error",
            }
        ]
    }, estado_http

def parse_iso_datetime(dt_str):
    if not isinstance(dt_str, str):
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None

def format_iso_datetime(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
        
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_ARG)
        
    return dt.isoformat()

def listar_reservas(limit, offset, id_cancha, id_socio, estado,  fecha_desde, fecha_hasta):
    where_clauses = []
    params = []

    if id_cancha:
        where_clauses.append("id_cancha = %s")
        params.append(id_cancha)

    if id_socio:
        where_clauses.append("id_socio = %s")
        params.append(id_socio)
        
    if estado:
        where_clauses.append("estado = %s")
        params.append(estado)

    if fecha_desde:
        dt_desde = parse_iso_datetime(fecha_desde)
        if not dt_desde:
            return respuesta_error(
                "ERROR_VALIDACION", "Formato inválido para fecha_desde", 400
            )
        where_clauses.append("fecha_hora_inicio >= %s")
        params.append(dt_desde)
        
    if fecha_hasta:
        dt_hasta = parse_iso_datetime(fecha_hasta)
        if not dt_hasta:
            return respuesta_error(
                "ERROR_VALIDACION", "Formato inválido para fecha_hasta", 400
            )
        where_clauses.append("fecha_hora_fin <= %s")
        params.append(dt_hasta)

    where_sql = (
       " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    )
        
    reservas, _total = obtener_con_filtros(where_sql, params, limit, offset)

    if not reservas:
        return None, 204

    for r in reservas:
        if r.get("fecha_hora_inicio"):
            r["fecha_hora_inicio"] = format_iso_datetime(r["fecha_hora_inicio"])
        if r.get("fecha_hora_fin"):
            r["fecha_hora_fin"] = format_iso_datetime(r["fecha_hora_fin"])

    return {"reservas": reservas}, 200


def obtener_por_id(reserva_id):
    reserva = obtener_reserva_por_id(reserva_id)

    if not reserva:
        return respuesta_error( 
            "RECURSO_NO_ENCONTRADO", "Reserva no encontrada", 404
        )

    if reserva.get("fecha_hora_inicio"):
        reserva["fecha_hora_inicio"] = format_iso_datetime(
            reserva["fecha_hora_inicio"]
        )
    if reserva.get("fecha_hora_fin"):
        reserva["fecha_hora_fin"] = format_iso_datetime(
            reserva["fecha_hora_fin"]
        )

    return reserva, 200


def crear_reserva(data):
    campos_obligatorios = ["id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"]
    for campo in campos_obligatorios:
        if campo not in data or data[campo] is None:
            return respuesta_error(
                "ERROR_VALIDACION", f"El campo '{campo}' es obligatorio", 400
            )
                             
    id_cancha = data.get("id_cancha")
    id_socio = data.get("id_socio")

    if isinstance(id_cancha, bool) or not isinstance(id_cancha, int) or id_cancha <= 0:
        return respuesta_error(
            "ERROR_VALIDACION", "id_cancha debe ser un entero positivo", 400
        )

    if isinstance(id_socio, bool) or not isinstance(id_socio, int) or id_socio <= 0:
        return respuesta_error(
            "ERROR_VALIDACION", "id_socio debe ser un entero positivo", 400
        )

    fecha_hora_inicio = parse_iso_datetime(data.get("fecha_hora_inicio"))
    fecha_hora_fin = parse_iso_datetime(data.get("fecha_hora_fin"))

    if fecha_hora_inicio.time().minute != 0 or fecha_hora_fin.time().minute != 0:
        return respuesta_error(
            "ERROR_VALIDACION",
            "Las fechas deben ser ISO 8601 válidas con zona horaria (-03:00)",
            400,
        )

    ahora = datetime.now(TZ_ARG)
    if fecha_hora_inicio <= ahora:
        return respuesta_error(
            "ERROR_VALIDACION", "La reserva debe ser en el futuro", 400
        )

    if fecha_hora_inicio.date() != fecha_hora_fin.date():
        return respuesta_error(
            "ERROR_VALIDACION",
            "La reserva debe comenzar y terminar el mismo día",
            400,
        )
        
    diferencia = fecha_hora_fin - fecha_hora_inicio 
    duracion_horas = diferencia.total_seconds() / 3600.0 

    if duracion_horas not in [1.0, 2.0, 3.0]:
        return respuesta_error(
            "ERROR_VALIDACION",
            "la duracion de la reserva debe ser de 1, 2 o 3 horas exactas",
            400,
        )

    if (
        fecha_hora_inicio.time() < HORA_APERTURA 
        or fecha_hora_fin.time() > HORA_CIERRE
    ):
        return respuesta_error(
            "ERROR_VALIDACION",
            "La reserva está fuera del horario del club (08:00 a 23:00)",
            400,
        )

    cancha = obtener_cancha(id_cancha)
    if not cancha:
        return respuesta_error(
            "RECURSO_NO_ENCONTRADO", "Cancha no encontrada", 404
        )

    if not cancha.get("activa", True):
        return respuesta_error(
            "ERROR_VALIDACION", "La cancha especificada no está activa", 400
        )

    socio = obtener_socio(id_socio)
    if not socio:
        return respuesta_error(
            "RECURSO_NO_ENCONTRADO", "Socio no encontrado", 404
        )

    if not socio.get("activo", True):
        return respuesta_error(
            "ERROR_VALIDACION", "El socio especificado no está activo", 400
        )

    if verificar_superposicion_cancha(
        id_cancha, fecha_hora_inicio, fecha_hora_fin
    ):
        return respuesta_error(
            "RECURSO_SUPERPUESTO",
            "La cancha ya se encuentra reservada en ese horario",
            409,
        )
        
    if verificar_superposicion_socio(
        id_socio, fecha_hora_inicio, fecha_hora_fin
    ):
        return respuesta_error(
            "RECURSO_SUPERPUESTO",
            "El socio ya posee una reserva confirmada en ese horario",
            409,
        )

    precio_hora = cancha["precio_hora"]
    precio_total = precio_hora * int(duracion_horas)

    reserva_id = crear_en_repo(
        id_cancha=id_cancha,
        id_socio=id_socio,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        tarifa_historica=precio_hora,
        total=precio_total,
    )

    reserva_creada = obtener_reserva_por_id(reserva_id)
    if reserva_creada:
        reserva_creada["fecha_hora_inicio"] = format_iso_datetime(
            reserva_creada["fecha_hora_inicio"]
        )
        reserva_creada["fecha_hora_fin"] = format_iso_datetime(
            reserva_creada["fecha_hora_fin"]
        )
        return reserva_creada, 201
        
    return {
        "id": reserva_id,
        "id_cancha": id_cancha,
        "id_socio": id_socio,
        "fecha_hora_inicio": format_iso_datetime(fecha_hora_inicio),
        "fecha_hora_fin": format_iso_datetime(fecha_hora_fin),
        "estado": "confirmada",
        "precio_hora": precio_hora,
        "precio_total": precio_total,
    }, 201

def actualizar_estado(reserva_id, nuevo_estado):
    reserva = obtener_reserva_por_id(reserva_id)
    if not reserva:
        return respuesta_error( 
            "RECURSO_NO_ENCONTRADO", "Reserva no encontrada", 404
        )
        
    estado_actual = reserva["estado"]

    if estado_actual == nuevo_estado:
        reserva["fecha_hora_inicio"] = format_iso_datetime(reserva["fecha_hora_inicio"])
        reserva["fecha_hora_fin"] = format_iso_datetime(reserva["fecha_hora_fin"])
        return reserva, 200
        
    if estado_actual in {"cancelada", "finalizada"}:
        return respuesta_error(
            "RECURSO_SUPERPUESTO",
            f"No se puede cambiar el estado de una reserva '{estado_actual}'",
            409,
        )
    if nuevo_estado not in {"cancelada", "finalizada"}:
        return respuesta_error(
            "ERROR_VALIDACION", 
            "El nuevo estado solo puede ser 'cancelada' o 'finalizada'",
            400,
        )
    ahora = datetime.now(TZ_ARG)
    fecha_inicio = parse_iso_datetime(reserva["fecha_hora_inicio"]) if isinstance(reserva["fecha_hora_inicio"], str) else reserva["fecha_hora_inicio"]
    fecha_fin = parse_iso_datetime(reserva["fecha_hora_fin"]) if isinstance(reserva["fecha_hora_fin"], str) else reserva["fecha_hora_fin"]

    if nuevo_estado == "cancelada" and ahora >= fecha_inicio:
        return respuesta_error(
            "RECURSO_SUPERPUESTO",
            "Solo se pueden cancelar reservas antes de su hora de inicio", 
            409,
        )
    if nuevo_estado == "finalizada" and ahora < fecha_fin:
        return respuesta_error(
            "RECURSO_SUPERPUESTO",
            "Solo se pueden finalizar reservas una vez alcanzada la hora de fin",
            409, 
        )
    actualizar_estado_en_repo(reserva_id, nuevo_estado)
    reserva_actualizada = obtener_reserva_por_id(reserva_id) 

    if reserva_actualizada:
        reserva_actualizada["fecha_hora_inicio"] = format_iso_datetime(
            reserva_actualizada["fecha_hora_inicio"]
        )
        reserva_actualizada["fecha_hora_fin"] = format_iso_datetime(
            reserva_actualizada["fecha_hora_fin"]
        )
        return reserva_actualizada, 200
    return {"mensaje": "Estado de la reserva actualizado correctamente"}, 200
