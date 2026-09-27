import app.repositories.socios_repository as socios_repository
from app.validators.socios_validators import (
    validate_create_socio,
    validate_update_socio,
    validate_socios_filters
)
from app.validators.common_validators import make_error_response


def listar_socios(query_args, limit, offset):
    """Delega validación de filtros y recupera socios paginados."""
    resultado = None
    status = 200

    filters, err = validate_socios_filters(query_args)
    if err:
        resultado = err
        status = 400
    else:
        where_clauses = []
        params = []
        extra_params = {}

        if "nombre" in filters:
            where_clauses.append("LOWER(nombre) LIKE %s")
            params.append(f"%{filters['nombre'].lower()}%")
            extra_params["nombre"] = filters["nombre"]

        if "activo" in filters:
            where_clauses.append("activo = %s")
            params.append(1 if filters["activo"] else 0)
            extra_params["activo"] = "true" if filters["activo"] else "false"

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        socios, total = socios_repository.obtener_con_filtros(where_sql, params, limit, offset)

        for s in socios:
            s["activo"] = bool(s["activo"])

        resultado = {
            "socios": socios,
            "total": total,
            "extra_params": extra_params
        }
        status = 200

    return resultado, status


def obtener_por_id(socio_id):
    """Recupera un socio por ID con casteo booleano del campo activo."""
    resultado = None
    status = 200

    socio = socios_repository.obtener_por_id(socio_id)
    if not socio:
        resultado = make_error_response(
            "NOT_FOUND",
            "Socio no encontrado",
            description=f"No existe un socio con el id {socio_id}"
        )
        status = 404
    else:
        socio["activo"] = bool(socio["activo"])
        resultado = socio
        status = 200

    return resultado, status


def crear_socio(data):
    """
    Valida datos, verifica unicidad de email y persiste el socio.
    Retorna obligatoriamente status 201 en caso de éxito.
    """
    resultado = None
    status = 201

    cleaned, err = validate_create_socio(data)
    if err:
        resultado = err
        status = 400
    elif socios_repository.verificar_email_existente(cleaned["email"]):
        resultado = make_error_response(
            "CONFLICT",
            "El correo electrónico ya se encuentra registrado."
        )
        status = 409
    else:
        socio_id = socios_repository.crear(
            cleaned["nombre"],
            cleaned["email"],
            cleaned["activo"]
        )
        resultado, _ = obtener_por_id(socio_id)
        status = 201

    return resultado, status


def actualizar_socio(socio_id, data):
    """Actualiza parcialmente un socio asegurando que el nuevo correo no colisione."""
    resultado = None
    status = 200

    socio_actual = socios_repository.obtener_por_id(socio_id)
    if not socio_actual:
        resultado = make_error_response(
            "NOT_FOUND",
            "Socio no encontrado",
            description=f"No existe un socio con el id {socio_id}"
        )
        status = 404
    else:
        cleaned, err = validate_update_socio(data)
        if err:
            resultado = err
            status = 400
        else:
            email_colision = False
            if "email" in cleaned and cleaned["email"] != socio_actual["email"].lower():
                if socios_repository.verificar_email_existente(cleaned["email"], socio_id_excluir=socio_id):
                    email_colision = True

            if email_colision:
                resultado = make_error_response(
                    "CONFLICT",
                    "El correo electrónico ya se encuentra registrado por otro socio."
                )
                status = 409
            else:
                fields = []
                params = []

                if "nombre" in cleaned:
                    fields.append("nombre = %s")
                    params.append(cleaned["nombre"])

                if "email" in cleaned:
                    fields.append("email = %s")
                    params.append(cleaned["email"])

                if "activo" in cleaned:
                    fields.append("activo = %s")
                    params.append(1 if cleaned["activo"] else 0)

                socios_repository.actualizar(socio_id, fields, params)
                resultado, status = obtener_por_id(socio_id)

    return resultado, status