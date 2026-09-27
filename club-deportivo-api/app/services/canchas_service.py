import app.repositories.canchas_repository as canchas_repository
from app.validators.canchas_validators import (
    validate_create_cancha,
    validate_update_cancha,
    validate_canchas_filters,
    validate_disponibilidad_params
)
from app.validators.common_validators import make_error_response


def listar_canchas(query_args, limit, offset):
    """Delega validación y recupera canchas paginadas."""
    resultado = None
    status = 200

    filters, err = validate_canchas_filters(query_args)
    if err:
        resultado = err
        status = 400
    else:
        where_clauses = []
        params = []
        extra_params = {}

        if "id_deporte" in filters:
            where_clauses.append("id_deporte = %s")
            params.append(filters["id_deporte"])
            extra_params["id_deporte"] = filters["id_deporte"]

        if "nombre" in filters:
            where_clauses.append("LOWER(nombre) LIKE %s")
            params.append(f"%{filters['nombre'].lower()}%")
            extra_params["nombre"] = filters["nombre"]

        if "techada" in filters:
            where_clauses.append("techada = %s")
            params.append(1 if filters["techada"] else 0)
            extra_params["techada"] = "true" if filters["techada"] else "false"

        if "activa" in filters:
            where_clauses.append("activa = %s")
            params.append(1 if filters["activa"] else 0)
            extra_params["activa"] = "true" if filters["activa"] else "false"

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        canchas, total = canchas_repository.obtener_con_filtros(where_sql, params, limit, offset)

        for cancha in canchas:
            cancha["techada"] = bool(cancha["techada"])
            cancha["activa"] = bool(cancha["activa"])

        resultado = {
            "canchas": canchas,
            "total": total,
            "extra_params": extra_params
        }
        status = 200

    return resultado, status


def obtener_por_id(cancha_id):
    """Recupera cancha por clave primaria con casteo booleano."""
    cancha = canchas_repository.obtener_por_id(cancha_id)
    if cancha:
        cancha["techada"] = bool(cancha["techada"])
        cancha["activa"] = bool(cancha["activa"])
    return cancha


def crear_cancha(data):
    """Sanea datos, valida FK de deporte y persiste la nueva cancha."""
    resultado = None
    status = 201

    cleaned, err = validate_create_cancha(data)
    if err:
        resultado = err
        status = 400
    elif not canchas_repository.verificar_deporte(cleaned["id_deporte"]):
        resultado = make_error_response("NOT_FOUND", "El deporte especificado no existe.")
        status = 404
    else:
        cancha_id = canchas_repository.crear(
            cleaned["id_deporte"],
            cleaned["nombre"],
            cleaned["precio_hora"],
            cleaned["techada"],
            cleaned["activa"]
        )
        resultado = obtener_por_id(cancha_id)
        status = 201

    return resultado, status


def actualizar_cancha(cancha_id, data):
    """Actualiza parcialmente una cancha asegurando inmutabilidad de id_deporte."""
    resultado = None
    status = 200

    cancha_actual = canchas_repository.obtener_por_id(cancha_id)
    if not cancha_actual:
        resultado = make_error_response("NOT_FOUND", "Cancha no encontrada", description=f"No existe una cancha con el id {cancha_id}")
        status = 404
    else:
        cleaned, err = validate_update_cancha(data)
        if err:
            resultado = err
            status = 400
        else:
            fields = []
            params = []

            if "nombre" in cleaned:
                fields.append("nombre = %s")
                params.append(cleaned["nombre"])

            if "precio_hora" in cleaned:
                fields.append("precio_hora = %s")
                params.append(cleaned["precio_hora"])

            if "techada" in cleaned:
                fields.append("techada = %s")
                params.append(1 if cleaned["techada"] else 0)

            if "activa" in cleaned:
                fields.append("activa = %s")
                params.append(1 if cleaned["activa"] else 0)

            canchas_repository.actualizar(cancha_id, fields, params)
            resultado = obtener_por_id(cancha_id)
            status = 200

    return resultado, status


def eliminar_cancha(cancha_id):
    """Elimina físicamente únicamente si no tiene turnos asociados."""
    resultado = None
    status = 204

    cancha = canchas_repository.obtener_por_id(cancha_id)
    if not cancha:
        resultado = make_error_response("NOT_FOUND", "Cancha no encontrada", description=f"No existe una cancha con el id {cancha_id}")
        status = 404
    elif canchas_repository.verificar_reservas_asociadas(cancha_id):
        resultado = make_error_response(
            "CONFLICT",
            "No se puede eliminar una cancha con reservas asociadas (independientemente de su estado). Puede desactivarla mediante PATCH."
        )
        status = 409
    else:
        canchas_repository.eliminar(cancha_id)
        resultado = None
        status = 204

    return resultado, status


def obtener_canchas_disponibles(query_args, limit, offset):
    """Consulta turnos disponibles en el intervalo solicitado."""
    resultado = None
    status = 200

    filters, err = validate_disponibilidad_params(query_args)
    if err:
        resultado = err
        status = 400
    else:
        dt_inicio_db = filters["inicio_dt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        dt_fin_db = filters["fin_dt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        id_deporte = filters.get("id_deporte")
        techada = filters.get("techada")

        canchas, total = canchas_repository.obtener_canchas_disponibles(
            dt_inicio_db,
            dt_fin_db,
            id_deporte,
            techada,
            limit,
            offset
        )

        for cancha in canchas:
            cancha["techada"] = bool(cancha["techada"])
            cancha["activa"] = bool(cancha["activa"])

        extra_params = {
            "fecha": filters["fecha"],
            "hora_inicio": filters["hora_inicio"],
            "hora_fin": filters["hora_fin"]
        }
        if id_deporte is not None:
            extra_params["id_deporte"] = id_deporte
        if techada is not None:
            extra_params["techada"] = "true" if techada else "false"

        resultado = {
            "canchas": canchas,
            "total": total,
            "extra_params": extra_params
        }
        status = 200

    return resultado, status