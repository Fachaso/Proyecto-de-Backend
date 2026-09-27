"""
Validaciones transversales y comunes a todas las entidades del sistema.
"""


def make_error_response(code: str, message: str, level: str = "error", description: str = None) -> dict:
    """Construye la estructura de error homogénea utilizada por el grupo."""
    error_dict = {
        "code": code,
        "message": message,
        "level": level
    }
    if description:
        error_dict["description"] = description
    return {"errors": [error_dict]}


def reject_unknown_fields(data: dict, allowed_fields: set):
    """
    Rechaza con 400 Bad Request si el cuerpo JSON contiene campos no permitidos.
    Enunciado Página 4: 'Se rechazarán campos y parámetros desconocidos'.
    """
    res = None
    if not isinstance(data, dict):
        res = make_error_response("BAD_REQUEST", "El cuerpo de la solicitud debe ser un objeto JSON válido.")
    else:
        unknown = set(data.keys()) - allowed_fields
        if unknown:
            campos = ", ".join(sorted(unknown))
            res = make_error_response("BAD_REQUEST", f"Campos no permitidos en la solicitud: {campos}.")
    return res


def reject_unknown_query_params(query_args: dict, allowed_params: set):
    """
    Rechaza con 400 Bad Request si la query string incluye parámetros no contemplados.
    Enunciado Página 4: 'Se rechazarán campos y parámetros desconocidos'.
    """
    res = None
    if isinstance(query_args, dict):
        unknown = set(query_args.keys()) - allowed_params
        if unknown:
            params = ", ".join(sorted(unknown))
            res = make_error_response("BAD_REQUEST", f"Parámetros de consulta no permitidos: {params}.")
    return res


def validate_positive_id(value, entity_name: str = "recurso"):
    """
    Valida que un identificador numérico sea un entero estrictamente mayor que cero.
    Enunciado Página 4: 'Los identificadores serán enteros positivos'.
    """
    val = None
    err = None

    if isinstance(value, bool):
        err = make_error_response("BAD_REQUEST", f"El identificador de {entity_name} debe ser un número entero positivo.")
    else:
        try:
            id_num = int(value)
            if id_num <= 0:
                err = make_error_response("BAD_REQUEST", f"El identificador de {entity_name} debe ser mayor a cero.")
            else:
                val = id_num
        except (ValueError, TypeError):
            err = make_error_response("BAD_REQUEST", f"El identificador de {entity_name} debe ser un número entero positivo.")

    return val, err