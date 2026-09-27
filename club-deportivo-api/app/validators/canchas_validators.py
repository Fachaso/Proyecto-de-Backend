"""
Capa de Validación Sintáctica y de Tipos para Canchas.
"""
import re
from datetime import datetime, timezone, timedelta
from app.validators.common_validators import make_error_response, reject_unknown_fields

TZ_GMT3 = timezone(timedelta(hours=-3))

ALLOWED_POST_CANCHA_FIELDS = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
ALLOWED_PATCH_CANCHA_FIELDS = {"nombre", "precio_hora", "techada", "activa"}
ALLOWED_GET_CANCHAS_PARAMS = {"_limit", "_offset", "id_deporte", "nombre", "techada", "activa"}
ALLOWED_GET_DISPONIBLES_PARAMS = {"_limit", "_offset", "fecha", "hora_inicio", "hora_fin", "id_deporte", "techada"}


def validate_create_cancha(data: dict):
    """
    Valida la carga útil para POST /canchas.
    Obligatorios: nombre, id_deporte, precio_hora.
    Opcionales con defaults: techada (False), activa (True).
    Un único return al final.
    """
    cleaned = None
    err = reject_unknown_fields(data, ALLOWED_POST_CANCHA_FIELDS)

    if not err:
        nombre_raw = data.get("nombre")
        id_deporte = data.get("id_deporte")
        precio_hora = data.get("precio_hora")
        techada = data.get("techada", False)
        activa = data.get("activa", True)

        if not isinstance(nombre_raw, str) or not nombre_raw.strip():
            err = make_error_response("BAD_REQUEST", "El nombre es obligatorio y no puede quedar vacío.")
        elif isinstance(id_deporte, bool) or not isinstance(id_deporte, int) or id_deporte <= 0:
            err = make_error_response("BAD_REQUEST", "El campo id_deporte debe ser un entero positivo.")
        elif isinstance(precio_hora, bool) or not isinstance(precio_hora, int) or precio_hora <= 0:
            err = make_error_response("BAD_REQUEST", "El campo precio_hora debe ser un entero positivo en centavos.")
        elif not isinstance(techada, bool):
            err = make_error_response("BAD_REQUEST", "El campo techada debe ser un booleano (true o false).")
        elif not isinstance(activa, bool):
            err = make_error_response("BAD_REQUEST", "El campo activa debe ser un booleano (true o false).")
        else:
            cleaned = {
                "nombre": nombre_raw.strip(),
                "id_deporte": id_deporte,
                "precio_hora": precio_hora,
                "techada": techada,
                "activa": activa
            }

    return cleaned, err


def validate_update_cancha(data: dict):
    """
    Valida la carga útil para PATCH /canchas/{id}.
    Prohíbe id_deporte y campos desconocidos.
    Rechaza cuerpos vacíos.
    """
    cleaned = None
    err = None

    if not isinstance(data, dict):
        err = make_error_response("BAD_REQUEST", "El cuerpo debe ser un objeto JSON válido.")
    elif not data:
        err = make_error_response("BAD_REQUEST", "El cuerpo de la solicitud no puede estar vacío en una actualización.")
    else:
        err = reject_unknown_fields(data, ALLOWED_PATCH_CANCHA_FIELDS)
        if not err:
            temp_cleaned = {}

            if "nombre" in data and not err:
                nombre = data["nombre"]
                if not isinstance(nombre, str) or not nombre.strip():
                    err = make_error_response("BAD_REQUEST", "El nombre debe ser una cadena no vacía.")
                else:
                    temp_cleaned["nombre"] = nombre.strip()

            if "precio_hora" in data and not err:
                precio_hora = data["precio_hora"]
                if isinstance(precio_hora, bool) or not isinstance(precio_hora, int) or precio_hora <= 0:
                    err = make_error_response("BAD_REQUEST", "El precio_hora debe ser un entero positivo en centavos.")
                else:
                    temp_cleaned["precio_hora"] = precio_hora

            if "techada" in data and not err:
                techada = data["techada"]
                if not isinstance(techada, bool):
                    err = make_error_response("BAD_REQUEST", "El campo techada debe ser un booleano.")
                else:
                    temp_cleaned["techada"] = techada

            if "activa" in data and not err:
                activa = data["activa"]
                if not isinstance(activa, bool):
                    err = make_error_response("BAD_REQUEST", "El campo activa debe ser un booleano.")
                else:
                    temp_cleaned["activa"] = activa

            if not err:
                cleaned = temp_cleaned

    return cleaned, err


def validate_canchas_filters(args: dict):
    """Valida los filtros de búsqueda en GET /canchas."""
    filters = None
    err = None
    temp_filters = {}

    if "id_deporte" in args and args["id_deporte"]:
        try:
            val = int(args["id_deporte"])
            if val <= 0:
                err = make_error_response("BAD_REQUEST", "El filtro id_deporte debe ser un entero positivo.")
            else:
                temp_filters["id_deporte"] = val
        except (ValueError, TypeError):
            err = make_error_response("BAD_REQUEST", "El filtro id_deporte debe ser un entero positivo.")

    if not err and "nombre" in args and args["nombre"]:
        nombre_clean = args["nombre"].strip()
        if nombre_clean:
            temp_filters["nombre"] = nombre_clean

    if not err and "techada" in args and args["techada"]:
        v = args["techada"].strip().lower()
        if v in ("true", "false"):
            temp_filters["techada"] = (v == "true")
        else:
            err = make_error_response("BAD_REQUEST", "El filtro techada solo admite true o false.")

    if not err and "activa" in args and args["activa"]:
        v = args["activa"].strip().lower()
        if v in ("true", "false"):
            temp_filters["activa"] = (v == "true")
        else:
            err = make_error_response("BAD_REQUEST", "El filtro activa solo admite true o false.")

    if not err:
        filters = temp_filters

    return filters, err


def validate_disponibilidad_params(args: dict):
    """
    Valida parámetros de GET /canchas/disponibles.
    """
    filters = None
    err = None

    for campo in ["fecha", "hora_inicio", "hora_fin"]:
        if not err and (campo not in args or not str(args[campo]).strip()):
            err = make_error_response("BAD_REQUEST", f"El parámetro '{campo}' es obligatorio.")

    fecha_obj = None
    if not err:
        try:
            fecha_obj = datetime.strptime(str(args["fecha"]).strip(), "%Y-%m-%d").date()
        except ValueError:
            err = make_error_response("BAD_REQUEST", "Formato de fecha inválido. Se espera YYYY-MM-DD.")

    time_regex = re.compile(r"^(\d{2}):(\d{2})(?::(\d{2}))?$")
    m_ini = None
    m_fin = None
    if not err:
        m_ini = time_regex.match(str(args["hora_inicio"]).strip())
        m_fin = time_regex.match(str(args["hora_fin"]).strip())
        if not m_ini or not m_fin:
            err = make_error_response("BAD_REQUEST", "Formato de hora inválido. Se espera HH:MM o HH:MM:SS.")

    dt_inicio = None
    dt_fin = None
    if not err:
        h_ini, min_ini = int(m_ini.group(1)), int(m_ini.group(2))
        h_fin, min_fin = int(m_fin.group(1)), int(m_fin.group(2))
        sec_ini = int(m_ini.group(3)) if m_ini.group(3) else 0
        sec_fin = int(m_fin.group(3)) if m_fin.group(3) else 0

        if min_ini != 0 or min_fin != 0 or sec_ini != 0 or sec_fin != 0:
            err = make_error_response("BAD_REQUEST", "Las reservas deben comenzar y terminar en horas en punto (:00:00).")
        else:
            dt_inicio = datetime(fecha_obj.year, fecha_obj.month, fecha_obj.day, h_ini, 0, 0, 0, tzinfo=TZ_GMT3)
            dt_fin = datetime(fecha_obj.year, fecha_obj.month, fecha_obj.day, h_fin, 0, 0, 0, tzinfo=TZ_GMT3)
            ahora = datetime.now(TZ_GMT3)

            if dt_inicio <= ahora:
                err = make_error_response("BAD_REQUEST", "El inicio del intervalo debe ser posterior al momento actual.")
            elif dt_inicio >= dt_fin:
                err = make_error_response("BAD_REQUEST", "La hora de inicio debe ser estrictamente menor que la hora de fin.")
            elif dt_inicio.hour < 8 or dt_fin.hour > 23 or (dt_fin.hour == 23 and dt_fin.minute > 0):
                err = make_error_response("BAD_REQUEST", "El intervalo debe quedar dentro del horario del club (08:00 a 23:00).")
            else:
                duracion_horas = (dt_fin - dt_inicio).total_seconds() / 3600.0
                if duracion_horas not in (1.0, 2.0, 3.0):
                    err = make_error_response("BAD_REQUEST", "La duración debe ser de entre 1 y 3 horas completas.")

    if not err:
        temp_filters = {
            "inicio_dt": dt_inicio,
            "fin_dt": dt_fin,
            "fecha": str(args["fecha"]).strip(),
            "hora_inicio": str(args["hora_inicio"]).strip(),
            "hora_fin": str(args["hora_fin"]).strip()
        }

        if "id_deporte" in args and args["id_deporte"]:
            try:
                val = int(args["id_deporte"])
                if val <= 0:
                    err = make_error_response("BAD_REQUEST", "El filtro id_deporte debe ser un entero positivo.")
                else:
                    temp_filters["id_deporte"] = val
            except (ValueError, TypeError):
                err = make_error_response("BAD_REQUEST", "El filtro id_deporte debe ser un entero positivo.")

        if not err and "techada" in args and args["techada"]:
            v = args["techada"].strip().lower()
            if v in ("true", "false"):
                temp_filters["techada"] = (v == "true")
            else:
                err = make_error_response("BAD_REQUEST", "El filtro techada solo admite true o false.")

        if not err:
            filters = temp_filters

    return filters, err