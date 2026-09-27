from datetime import datetime, timezone, timedelta
import app.repositories.reservas_repository as reservas_repository
from app.validators.reservas_validators import (
    TZ_GMT3,
    validate_create_reserva,
    validate_update_estado,
    validate_reservas_filters,
)
from app.validators.common_validators import make_error_response


def format_datetime_to_iso_gmt3(val):
    """
    Normaliza marcas temporales al formato estricto ISO 8601 GMT-3 con microsegundos:
    YYYY-MM-DDTHH:MM:SS.ffffff-03:00.
    """
    res = None
    if isinstance(val, str):
        try:
            val = datetime.fromisoformat(val)
        except ValueError:
            pass

    if isinstance(val, datetime):
        val_aware = val.replace(tzinfo=TZ_GMT3) if val.tzinfo is None else val.astimezone(TZ_GMT3)
        res = val_aware.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")
    else:
        res = str(val)

    return res


def serialize_reserva(reserva: dict):
    """Aplica serialización ISO GMT-3 a los campos temporales de una reserva."""
    item = None
    if reserva is not None:
        item = dict(reserva)
        item["fecha_hora_inicio"] = format_datetime_to_iso_gmt3(item["fecha_hora_inicio"])
        item["fecha_hora_fin"] = format_datetime_to_iso_gmt3(item["fecha_hora_fin"])
    return item


def listar_reservas(query_args: dict, limit: int, offset: int):
    """
    Recupera reservas paginadas aplicando filtros de búsqueda validados.
    """
    resultado = None
    status = 200

    filters, err = validate_reservas_filters(query_args)
    if err:
        resultado = err
        status = 400
    else:
        where_clauses = []
        params = []
        extra_params = {}

        if "id_cancha" in filters:
            where_clauses.append("id_cancha = %s")
            params.append(filters["id_cancha"])
            extra_params["id_cancha"] = filters["id_cancha"]

        if "id_socio" in filters:
            where_clauses.append("id_socio = %s")
            params.append(filters["id_socio"])
            extra_params["id_socio"] = filters["id_socio"]

        if "estado" in filters:
            where_clauses.append("estado = %s")
            params.append(filters["estado"])
            extra_params["estado"] = filters["estado"]

        if "fecha_desde" in filters:
            where_clauses.append("DATE(fecha_hora_inicio) >= %s")
            params.append(filters["fecha_desde"])
            extra_params["fecha_desde"] = filters["fecha_desde"]

        if "fecha_hasta" in filters:
            where_clauses.append("DATE(fecha_hora_inicio) <= %s")
            params.append(filters["fecha_hasta"])
            extra_params["fecha_hasta"] = filters["fecha_hasta"]

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        reservas_raw, total = reservas_repository.obtener_con_filtros(where_sql, params, limit, offset)

        reservas = [serialize_reserva(r) for r in reservas_raw]
        resultado = {
            "reservas": reservas,
            "total": total,
            "extra_params": extra_params
        }
        status = 200

    return resultado, status


def obtener_por_id(reserva_id: int):
    """Recupera una reserva por ID con formato ISO GMT-3."""
    resultado = None
    status = 200

    reserva = reservas_repository.obtener_por_id(reserva_id)
    if not reserva:
        resultado = make_error_response(
            "NOT_FOUND",
            "Reserva no encontrada",
            description=f"No existe una reserva con el id {reserva_id}"
        )
        status = 404
    else:
        resultado = serialize_reserva(reserva)
        status = 200

    return resultado, status


def crear_reserva(data: dict):
    """
    Crea una nueva reserva validando:
    - Formato ISO 8601 GMT-3 estricto, horas en punto, límites 08 a 23 y duración 1 a 3 hs.
    - Existencia y estado activo de cancha y socio (Página 7).
    - Superposición horaria en la cancha y en la agenda del socio.
    - Congelamiento inmutable de tarifa e importe total.
    """
    resultado = None
    status = 201

    cleaned, err = validate_create_reserva(data)
    if err:
        resultado = err
        status = 400
    else:
        cancha = reservas_repository.obtener_cancha(cleaned["id_cancha"])
        if not cancha:
            resultado = make_error_response(
                "NOT_FOUND",
                "Cancha no encontrada",
                description=f"La cancha con id {cleaned['id_cancha']} no existe."
            )
            status = 404
        elif not cancha["activa"]:
            resultado = make_error_response(
                "BAD_REQUEST",
                f"La cancha '{cancha['nombre']}' se encuentra inactiva y no admite nuevas reservas."
            )
            status = 400
        else:
            socio = reservas_repository.obtener_socio(cleaned["id_socio"])
            if not socio:
                resultado = make_error_response(
                    "NOT_FOUND",
                    "Socio no encontrado",
                    description=f"El socio con id {cleaned['id_socio']} no existe."
                )
                status = 404
            elif not socio["activo"]:
                resultado = make_error_response(
                    "BAD_REQUEST",
                    f"El socio '{socio['nombre']}' se encuentra inactivo y no puede realizar reservas."
                )
                status = 400
            elif reservas_repository.verificar_superposicion_cancha(
                cleaned["id_cancha"], cleaned["dt_inicio"], cleaned["dt_fin"]
            ):
                resultado = make_error_response(
                    "CONFLICT",
                    "La cancha ya se encuentra reservada en el intervalo horario solicitado."
                )
                status = 409
            elif reservas_repository.verificar_superposicion_socio(
                cleaned["id_socio"], cleaned["dt_inicio"], cleaned["dt_fin"]
            ):
                resultado = make_error_response(
                    "CONFLICT",
                    "El socio ya posee otra reserva confirmada superpuesta en ese mismo horario."
                )
                status = 409
            else:
                tarifa_historica = cancha["precio_hora"]
                total = tarifa_historica * cleaned["horas"]

                reserva_id = reservas_repository.crear(
                    cleaned["id_cancha"],
                    cleaned["id_socio"],
                    cleaned["dt_inicio"],
                    cleaned["dt_fin"],
                    tarifa_historica,
                    total,
                )
                resultado, status = obtener_por_id(reserva_id)
                status = 201

    return resultado, status


def actualizar_estado(reserva_id: int, data: dict):
    """
    Ejecuta transiciones de estado aplicando la máquina de estados oficial:
    - Idempotencia: repetir el estado actual devuelve 200 OK sin modificaciones.
    - confirmada -> cancelada: solo si inicio > ahora (turno futuro).
    - confirmada -> finalizada: solo si fin <= ahora (turno concluido).
    - Canceladas o finalizadas no pueden reactivarse ni cambiar de estado (409 Conflict).
    """
    resultado = None
    status = 200

    nuevo_estado, err = validate_update_estado(data)
    if err:
        resultado = err
        status = 400
    else:
        reserva = reservas_repository.obtener_por_id(reserva_id)
        if not reserva:
            resultado = make_error_response(
                "NOT_FOUND",
                "Reserva no encontrada",
                description=f"No existe una reserva con el id {reserva_id}"
            )
            status = 404
        else:
            estado_actual = reserva["estado"]

            # Regla de idempotencia oficial (Página 3): repetir estado devuelve éxito
            if nuevo_estado == estado_actual:
                resultado = serialize_reserva(reserva)
                status = 200
            elif estado_actual != "confirmada":
                resultado = make_error_response(
                    "CONFLICT",
                    f"No se permite modificar el estado de una reserva que ya está en '{estado_actual}'."
                )
                status = 409
            else:
                ahora = datetime.now(TZ_GMT3)

                dt_inicio = reserva["fecha_hora_inicio"]
                if isinstance(dt_inicio, str):
                    dt_inicio = datetime.fromisoformat(dt_inicio)
                if dt_inicio.tzinfo is None:
                    dt_inicio = dt_inicio.replace(tzinfo=TZ_GMT3)

                dt_fin = reserva["fecha_hora_fin"]
                if isinstance(dt_fin, str):
                    dt_fin = datetime.fromisoformat(dt_fin)
                if dt_fin.tzinfo is None:
                    dt_fin = dt_fin.replace(tzinfo=TZ_GMT3)

                if nuevo_estado == "cancelada":
                    if ahora >= dt_inicio:
                        resultado = make_error_response(
                            "CONFLICT",
                            "No es posible cancelar la reserva: el horario de inicio ya fue alcanzado o superado."
                        )
                        status = 409
                    else:
                        reservas_repository.actualizar_estado(reserva_id, "cancelada")
                        resultado, status = obtener_por_id(reserva_id)
                elif nuevo_estado == "finalizada":
                    if ahora < dt_fin:
                        resultado = make_error_response(
                            "CONFLICT",
                            "No es posible marcar la reserva como finalizada antes de que concluya el horario de fin."
                        )
                        status = 409
                    else:
                        reservas_repository.actualizar_estado(reserva_id, "finalizada")
                        resultado, status = obtener_por_id(reserva_id)
                else:
                    resultado = make_error_response(
                        "CONFLICT",
                        f"Transición de estado no permitida desde '{estado_actual}' hacia '{nuevo_estado}'."
                    )
                    status = 409

    return resultado, status