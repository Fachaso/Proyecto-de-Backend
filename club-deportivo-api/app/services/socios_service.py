import app.repositories.socios_repository as socios_repository

def listar_socios(limit,offset,nombre,activo,):
    where_clauses = []
    params = []
    extra_params = {}

    if nombre:
        where_clauses.append("LOWER(nombre) LIKE %s")
        params.append(f"%{nombre.lower()}%")
        extra_params['nombre'] = nombre


    if activo is not None:
        if activo not in ['true', 'false']:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "activo debe ser true o false",
                        "level": "error"
                    }
                ]
            }, 400

        where_clauses.append("activo = %s")
        params.append(1 if activo == 'true' else 0)
        extra_params['activo'] = activo

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    socios, total = socios_repository.obtener_con_filtros(where_sql, params, limit, offset)

    if not socios:
        return None, 204

    for s in socios:
        s['activo'] = bool(s['activo'])

    return {
        "socios": socios,
        "total": total,
        "extra_params": extra_params,
    }, 200

def obtener_por_id(socio_id):
    socio = socios_repository.obtener_por_id(socio_id)
    if not socio:
        return {
            "errors": [
                {
                    "code": "NOT_FOUND",
                    "message": "Socio no encontrado",
                    "level": "error"
                }
            ]
        }, 404

    socio['activo'] = bool(socio['activo'])
    return socio, 200

def crear_socio(data):
    campos_permitidos = {
        "nombre",
        "email",
    }

    for campo in data:
        if campo not in campos_permitidos:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": f"Campo desconocido: {campo}",
                        "level": "error"
                    }
                ]
            }, 400

    if (
        "nombre" not in data
        or "email" not in data
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Campos obligatorios faltantes",
                    "level": "error"
                }
            ]
        }, 400

    nombre = data["nombre"]
    email = data["email"]

    if not isinstance(nombre, str):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "nombre debe ser un string",
                    "level": "error"
                }
            ]
        }, 400

    if not isinstance(email, str):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "email debe ser un string",
                    "level": "error"
                }
            ]
        }, 400

    nombre = nombre.strip()
    email = email.strip().lower()

    if not nombre:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El nombre no puede estar vacío",
                    "level": "error"
                }
            ]
        }, 400

    partes_email = email.split("@")

    if (
        len(partes_email) != 2
        or not partes_email[0]
        or "." not in partes_email[1]
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El email tiene un formato inválido",
                    "level": "error"
                }
            ]
        }, 400

    if socios_repository.verificar_email_existente(
        email
    ):
        return {
            "errors": [
                {
                    "code": "CONFLICT",
                    "message": "El correo electrónico ya se encuentra registrado",
                    "level": "error"
                }
            ]
        }, 409

    activo = True

    socio_id = socios_repository.crear(
        nombre,
        email,
        activo,
    )

    return {
        "id": socio_id,
        "nombre": nombre,
        "email": email,
        "activo": activo,
    }, 201


def actualizar_socio(socio_id, data):
    socio = socios_repository.obtener_por_id(
        socio_id
    )

    if not socio:
        return {
            "errors": [
                {
                    "code": "NOT_FOUND",
                    "message": "Socio no encontrado",
                    "level": "error"
                }
            ]
        }, 404

    if not data:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El cuerpo no puede estar vacío",
                    "level": "error"
                }
            ]
        }, 400

    campos_permitidos = {
        "nombre",
        "email",
        "activo",
    }

    for campo in data:
        if campo not in campos_permitidos:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": f"Campo desconocido: {campo}",
                        "level": "error"
                    }
                ]
            }, 400

    nombre = socio["nombre"]
    email = socio["email"]
    activo = bool(socio["activo"])

    if "nombre" in data:
        if not isinstance(data["nombre"], str):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "nombre debe ser un string",
                        "level": "error"
                    }
                ]
            }, 400

        nombre = data["nombre"].strip()

        if not nombre:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "El nombre no puede estar vacío",
                        "level": "error"
                    }
                ]
            }, 400

    if "email" in data:
        if not isinstance(data["email"], str):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "email debe ser un string",
                        "level": "error"
                    }
                ]
            }, 400

        email = data["email"].strip().lower()

        partes_email = email.split("@")

        if (
            len(partes_email) != 2
            or not partes_email[0]
            or "." not in partes_email[1]
        ):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "El email tiene un formato inválido",
                        "level": "error"
                    }
                ]
            }, 400

        if (
            email != socio["email"].lower()
            and socios_repository.verificar_email_existente(
                email
            )
        ):
            return {
                "errors": [
                    {
                        "code": "CONFLICT",
                        "message": "El correo electrónico ya se encuentra registrado",
                        "level": "error"
                    }
                ]
            }, 409

    if "activo" in data:
        if type(data["activo"]) is not bool:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "activo debe ser un booleano",
                        "level": "error"
                    }
                ]
            }, 400

        activo = data["activo"]

    socios_repository.actualizar(
        socio_id,
        nombre,
        email,
        activo,
    )

    return None, 204