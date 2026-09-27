import re
from datetime import datetime, timezone, timedelta
from app.validators.common_validators import make_error_response, reject_unknown_fields

TZ_GMT3 = timezone(timedelta(hours=-3))

ISO_GMT3_REGEX = re.compile(
    r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{6})-03:00$"
)

ALLOWED_POST_RESERVA_FIELDS = {
    "id_socio",
    "id_cancha",
    "fecha_hora_inicio",
    "fecha_hora_fin",
}
ALLOWED_PUT_ESTADO_FIELDS = {"estado"}
ALLOWED_GET_RESERVAS_PARAMS = {
    "_limit",
    "_offset",
    "id_cancha",
    "id_socio",
    "estado",
    "fecha_desde",
    "fecha_hasta",
}
ALLOWED_ESTADOS = {"confirmada", "cancelada", "finalizada"}


def parse_and_validate_iso_gmt3(date_str: str, field_name: str):
    """
    Valida el formato estricto ISO 8601 GMT-3 con 6 microsegundos.
    Verifica que el turno inicie o finalice exactamente en horas en punto (:00:00.000000).
    """
    dt = None
    err = None

    if not isinstance(date_str, str):
        err = make_error_response(
            "BAD_REQUEST",
            f"El campo '{field_name}' debe ser una cadena de texto."
        )
    else:
        m = ISO_GMT3_REGEX.match(date_str)
        if not m:
            err = make_error_response(
                "BAD_REQUEST",
                f"El campo '{field_name}' debe cumplir el formato estricto ISO 8601 GMT-3 "
                f"'YYYY-MM-DDTHH:MM:SS.ffffff-03:00' con 6 microsegundos y desplazamiento -03:00."
            )
        else:
            _, mn, sc, mic = (
                m.group(2),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(5)),
            )
            if mn != 0 or sc != 0 or mic != 0:
                err = make_error_response(
                    "BAD_REQUEST",
                    f"El campo '{field_name}' debe comenzar y terminar exactamente en horas en punto (:00:00.000000)."
                )
            else:
                try:
                    dt = datetime.fromisoformat(date_str)
                except ValueError:
                    err = make_error_response(
                        "BAD_REQUEST",
                        f"El campo '{field_name}' no representa una fecha válida en el calendario."
                    )

    return dt, err


def validate_interval_rules(dt_inicio: datetime, dt_fin: datetime):
    """
    Valida las reglas temporales normativas del club:
    - Inicio estrictamente posterior al momento actual (futuro).
    - fecha_hora_inicio < fecha_hora_fin.
    - Mismo día calendario (no puede cruzar la medianoche).
    - Horario comprendido entre las 08:00 y las 23:00.
    - Duración entre 1 y 3 horas completas (1, 2 o 3 horas).
    """
    err = None
    ahora = datetime.now(TZ_GMT3)

    if dt_inicio <= ahora:
        err = make_error_response(
            "BAD_REQUEST",
            "Solo se pueden crear reservas cuyo inicio sea posterior al momento actual."
        )
    elif dt_inicio >= dt_fin:
        err = make_error_response(
            "BAD_REQUEST",
            "La fecha_hora_inicio debe ser estrictamente menor que fecha_hora_fin."
        )
    elif dt_inicio.date() != dt_fin.date():
        err = make_error_response(
            "BAD_REQUEST",
            "La reserva debe iniciar y finalizar dentro del mismo día calendario (no cruza la medianoche)."
        )
    elif dt_inicio.hour < 8 or dt_fin.hour > 23 or (dt_fin.hour == 23 and dt_fin.minute > 0):
        err = make_error_response(
            "BAD_REQUEST",
            "El intervalo completo de la reserva debe quedar comprendido entre las 08:00 y las 23:00."
        )
    else:
        duracion_horas = (dt_fin - dt_inicio).total_seconds() / 3600.0
        if duracion_horas not in (1.0, 2.0, 3.0):
            err = make_error_response(
                "BAD_REQUEST",
                "Las reservas deben durar exactamente entre una y tres horas completas (1, 2 o 3 horas)."
            )

    return err


def validate_create_reserva(data: dict):
    """
    Valida la carga útil para POST /reservas.
    Obligatorios: id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin.
    Rechaza campos desconocidos con 400 Bad Request.
    """
    cleaned = None
    err = reject_unknown_fields(data, ALLOWED_POST_RESERVA_FIELDS)

    if not err:
        missing = [f for f in ["id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"] if f not in data]
        if missing:
            err = make_error_response(
                "BAD_REQUEST",
                f"Campos obligatorios faltantes: {', '.join(missing)}."
            )
        else:
            id_socio = data["id_socio"]
            id_cancha = data["id_cancha"]

            if isinstance(id_socio, bool) or not isinstance(id_socio, int) or id_socio <= 0:
                err = make_error_response(
                    "BAD_REQUEST",
                    "El campo id_socio debe ser un entero positivo."
                )
            elif isinstance(id_cancha, bool) or not isinstance(id_cancha, int) or id_cancha <= 0:
                err = make_error_response(
                    "BAD_REQUEST",
                    "El campo id_cancha debe ser un entero positivo."
                )
            else:
                dt_inicio, err_inicio = parse_and_validate_iso_gmt3(
                    data["fecha_hora_inicio"], "fecha_hora_inicio"
                )
                if err_inicio:
                    err = err_inicio
                else:
                    dt_fin, err_fin = parse_and_validate_iso_gmt3(
                        data["fecha_hora_fin"], "fecha_hora_fin"
                    )
                    if err_fin:
                        err = err_fin
                    else:
                        err_interval = validate_interval_rules(dt_inicio, dt_fin)
                        if err_interval:
                            err = err_interval
                        else:
                            horas = int((dt_fin - dt_inicio).total_seconds() // 3600)
                            cleaned = {
                                "id_socio": id_socio,
                                "id_cancha": id_cancha,
                                "dt_inicio": dt_inicio,
                                "dt_fin": dt_fin,
                                "horas": horas,
                            }

    return cleaned, err


def validate_update_estado(data: dict):
    """
    Valida la carga útil para PUT /reservas/{id}/estado.
    Rechaza cuerpos vacíos y campos no admitidos.
    Aplica el principio de salida única (un único return).
    """
    nuevo_estado = None
    err = None

    if not isinstance(data, dict):
        err = make_error_response(
            "BAD_REQUEST",
            "El cuerpo de la solicitud debe ser un objeto JSON válido."
        )
    elif not data:
        err = make_error_response(
            "BAD_REQUEST",
            "El cuerpo de la solicitud no puede estar vacío."
        )
    else:
        err = reject_unknown_fields(data, ALLOWED_PUT_ESTADO_FIELDS)
        if not err:
            if "estado" not in data:
                err = make_error_response(
                    "BAD_REQUEST",
                    "El campo 'estado' es obligatorio."
                )
            else:
                raw_estado = data["estado"]
                if not isinstance(raw_estado, str) or raw_estado.strip().lower() not in ALLOWED_ESTADOS:
                    err = make_error_response(
                        "BAD_REQUEST",
                        f"Estado desconocido o inválido. Valores admitidos: {', '.join(sorted(ALLOWED_ESTADOS))}."
                    )
                else:
                    nuevo_estado = raw_estado.strip().lower()

    return nuevo_estado, err


def validate_reservas_filters(args: dict):
    """
    Valida los filtros de búsqueda para GET /reservas.
    Filtros opcionales: id_cancha, id_socio, estado, fecha_desde, fecha_hasta.
    Valida que fecha_desde <= fecha_hasta si ambos están presentes.
    Aplica el principio de salida única (un único return).
    """
    filters = None
    err = None
    temp_filters = {}

    if "id_cancha" in args and args["id_cancha"]:
        try:
            val_cancha = int(args["id_cancha"])
            if val_cancha <= 0:
                err = make_error_response(
                    "BAD_REQUEST",
                    "El filtro id_cancha debe ser un entero positivo."
                )
            else:
                temp_filters["id_cancha"] = val_cancha
        except (ValueError, TypeError):
            err = make_error_response(
                "BAD_REQUEST",
                "El filtro id_cancha debe ser un entero positivo."
            )

    if not err and "id_socio" in args and args["id_socio"]:
        try:
            val_socio = int(args["id_socio"])
            if val_socio <= 0:
                err = make_error_response(
                    "BAD_REQUEST",
                    "El filtro id_socio debe ser un entero positivo."
                )
            else:
                temp_filters["id_socio"] = val_socio
        except (ValueError, TypeError):
            err = make_error_response(
                "BAD_REQUEST",
                "El filtro id_socio debe ser un entero positivo."
            )

    if not err and "estado" in args and args["estado"]:
        est = str(args["estado"]).strip().lower()
        if est not in ALLOWED_ESTADOS:
            err = make_error_response(
                "BAD_REQUEST",
                f"Filtro 'estado' inválido. Opciones permitidas: {', '.join(sorted(ALLOWED_ESTADOS))}."
            )
        else:
            temp_filters["estado"] = est

    fecha_d = None
    fecha_h = None

    if not err and "fecha_desde" in args and args["fecha_desde"]:
        try:
            fecha_d = datetime.strptime(str(args["fecha_desde"]).strip(), "%Y-%m-%d").date()
            temp_filters["fecha_desde"] = str(fecha_d)
        except ValueError:
            err = make_error_response(
                "BAD_REQUEST",
                "El filtro fecha_desde debe tener formato YYYY-MM-DD."
            )

    if not err and "fecha_hasta" in args and args["fecha_hasta"]:
        try:
            fecha_h = datetime.strptime(str(args["fecha_hasta"]).strip(), "%Y-%m-%d").date()
            temp_filters["fecha_hasta"] = str(fecha_h)
        except ValueError:
            err = make_error_response(
                "BAD_REQUEST",
                "El filtro fecha_hasta debe tener formato YYYY-MM-DD."
            )

    if not err and fecha_d and fecha_h and fecha_d > fecha_h:
        err = make_error_response(
            "BAD_REQUEST",
            "El filtro fecha_desde debe ser menor o igual a fecha_hasta."
        )

    if not err:
        filters = temp_filters

    return filters, err