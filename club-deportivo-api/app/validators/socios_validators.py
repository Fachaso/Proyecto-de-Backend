"""
Capa de Validación Sintáctica y de Tipos para Socios.
"""
import re
from app.validators.common_validators import make_error_response, reject_unknown_fields

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

ALLOWED_POST_SOCIO_FIELDS = {"nombre", "email"}
ALLOWED_PATCH_SOCIO_FIELDS = {"nombre", "email", "activo"}
ALLOWED_GET_SOCIOS_PARAMS = {"_limit", "_offset", "nombre", "activo"}


def validate_create_socio(data: dict):
    """
    Valida la carga útil para POST /socios.
    - Obligatorios: nombre y email.
    - El servidor asigna activo: true automáticamente.
    - Nombre no vacío tras strip().
    - Formato de email válido y normalizado en minúsculas sin espacios.
    """
    cleaned = None
    err = reject_unknown_fields(data, ALLOWED_POST_SOCIO_FIELDS)

    if not err:
        nombre_raw = data.get("nombre")
        email_raw = data.get("email")

        if not isinstance(nombre_raw, str) or not nombre_raw.strip():
            err = make_error_response(
                "BAD_REQUEST",
                "El campo 'nombre' es obligatorio y no puede quedar vacío."
            )
        elif not isinstance(email_raw, str) or not email_raw.strip():
            err = make_error_response(
                "BAD_REQUEST",
                "El campo 'email' es obligatorio y no puede quedar vacío."
            )
        else:
            email_clean = email_raw.strip().lower()
            if not EMAIL_REGEX.match(email_clean):
                err = make_error_response(
                    "BAD_REQUEST",
                    "El formato del correo electrónico proporcionado no es válido."
                )
            else:
                cleaned = {
                    "nombre": nombre_raw.strip(),
                    "email": email_clean,
                    "activo": True
                }

    return cleaned, err


def validate_update_socio(data: dict):
    """
    Valida la carga útil para PATCH /socios/{id}.
    Campos editables: nombre, email, activo.
    Rechaza cuerpos vacíos.
    Rechaza campos desconocidos.
    """
    cleaned = None
    err = None

    if not isinstance(data, dict):
        err = make_error_response("BAD_REQUEST", "El cuerpo debe ser un objeto JSON válido.")
    elif not data:
        err = make_error_response("BAD_REQUEST", "El cuerpo de la solicitud no puede estar vacío en una actualización.")
    else:
        err = reject_unknown_fields(data, ALLOWED_PATCH_SOCIO_FIELDS)
        if not err:
            temp_cleaned = {}

            if "nombre" in data and not err:
                nombre = data["nombre"]
                if not isinstance(nombre, str) or not nombre.strip():
                    err = make_error_response("BAD_REQUEST", "El campo 'nombre' debe ser una cadena de texto no vacía.")
                else:
                    temp_cleaned["nombre"] = nombre.strip()

            if "email" in data and not err:
                email = data["email"]
                if not isinstance(email, str) or not email.strip():
                    err = make_error_response("BAD_REQUEST", "El campo 'email' no puede quedar vacío.")
                else:
                    email_clean = email.strip().lower()
                    if not EMAIL_REGEX.match(email_clean):
                        err = make_error_response("BAD_REQUEST", "El formato del correo electrónico no es válido.")
                    else:
                        temp_cleaned["email"] = email_clean

            if "activo" in data and not err:
                activo = data["activo"]
                if not isinstance(activo, bool):
                    err = make_error_response("BAD_REQUEST", "El campo 'activo' debe ser estrictamente booleano (true o false).")
                else:
                    temp_cleaned["activo"] = activo

            if not err:
                cleaned = temp_cleaned

    return cleaned, err


def validate_socios_filters(args: dict):
    """
    Valida los filtros de búsqueda para GET /socios.
    Solo permite 'nombre' y 'activo' (el enunciado NO admite 'email' como filtro en query).
    """
    filters = None
    err = None
    temp_filters = {}

    if "nombre" in args and args["nombre"]:
        nombre_clean = str(args["nombre"]).strip()
        if nombre_clean:
            temp_filters["nombre"] = nombre_clean

    if "activo" in args and args["activo"]:
        v = str(args["activo"]).strip().lower()
        if v in ("true", "false"):
            temp_filters["activo"] = (v == "true")
        else:
            err = make_error_response("BAD_REQUEST", "El filtro 'activo' solo admite 'true' o 'false'.")

    if not err:
        filters = temp_filters

    return filters, err