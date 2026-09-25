from datetime import datetime, timedelta, timezone

import app.repositories.canchas_repository as canchas_repository


def listar_canchas(
    limit,
    offset,
    id_deporte,
    nombre,
    techada,
    activa,
):
    where_clauses = []
    params = []
    extra_params = {}

    if id_deporte:
        where_clauses.append("id_deporte = %s")
        params.append(id_deporte)
        extra_params["id_deporte"] = id_deporte

    if nombre:
        where_clauses.append("LOWER(nombre) LIKE %s")
        params.append(f"%{nombre.lower()}%")
        extra_params["nombre"] = nombre

    if techada in ["true", "false"]:
        where_clauses.append("techada = %s")
        params.append(
            1 if techada == "true" else 0
        )
        extra_params["techada"] = techada

    if activa in ["true", "false"]:
        where_clauses.append("activa = %s")
        params.append(
            1 if activa == "true" else 0
        )
        extra_params["activa"] = activa

    if where_clauses:
        where_sql = (
            " WHERE "
            + " AND ".join(where_clauses)
        )
    else:
        where_sql = ""

    canchas, total = (
        canchas_repository.obtener_con_filtros(
            where_sql,
            params,
            limit,
            offset,
        )
    )

    for cancha in canchas:
        cancha["techada"] = bool(
            cancha["techada"]
        )
        cancha["activa"] = bool(
            cancha["activa"]
        )

    return canchas, total, extra_params


def obtener_por_id(cancha_id):
    cancha = canchas_repository.obtener_por_id(
        cancha_id
    )

    if not cancha:
        return None

    cancha["techada"] = bool(
        cancha["techada"]
    )

    cancha["activa"] = bool(
        cancha["activa"]
    )

    return cancha


def crear_cancha(data):
    if not isinstance(data, dict):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El cuerpo debe ser un objeto JSON",
                    "level": "error",
                }
            ]
        }, 400

    campos_permitidos = {
        "nombre",
        "id_deporte",
        "precio_hora",
        "techada",
        "activa",
    }

    campos_desconocidos = (
        set(data.keys())
        - campos_permitidos
    )

    if campos_desconocidos:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Se enviaron campos desconocidos",
                    "level": "error",
                }
            ]
        }, 400

    nombre = str(
        data.get("nombre", "")
    ).strip()

    id_deporte = data.get(
        "id_deporte"
    )

    precio_hora = data.get(
        "precio_hora"
    )

    techada = data.get(
        "techada",
        False,
    )

    activa = data.get(
        "activa",
        True,
    )

    if (
        not nombre
        or id_deporte is None
        or precio_hora is None
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Campos obligatorios faltantes",
                    "level": "error",
                }
            ]
        }, 400

    if (
        type(id_deporte) is not int
        or id_deporte <= 0
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "id_deporte debe ser un entero positivo",
                    "level": "error",
                }
            ]
        }, 400

    if (
        type(precio_hora) is not int
        or precio_hora <= 0
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "precio_hora debe ser un entero positivo",
                    "level": "error",
                }
            ]
        }, 400

    if type(techada) is not bool:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "techada debe ser un booleano",
                    "level": "error",
                }
            ]
        }, 400

    if type(activa) is not bool:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "activa debe ser un booleano",
                    "level": "error",
                }
            ]
        }, 400

    if not canchas_repository.verificar_deporte(
        id_deporte
    ):
        return {
            "errors": [
                {
                    "code": "NOT_FOUND",
                    "message": "Deporte no encontrado",
                    "level": "error",
                }
            ]
        }, 404

    cancha_id = canchas_repository.crear(
        id_deporte,
        nombre,
        precio_hora,
        techada,
        activa,
    )

    return {
        "id": cancha_id,
        "id_deporte": id_deporte,
        "nombre": nombre,
        "precio_hora": precio_hora,
        "techada": techada,
        "activa": activa,
    }, 201


def actualizar_cancha(
    cancha_id,
    data,
):
    cancha_actual = (
        canchas_repository.obtener_por_id(
            cancha_id
        )
    )

    if not cancha_actual:
        return {
            "errors": [
                {
                    "code": "NOT_FOUND",
                    "message": "Cancha no encontrada",
                    "level": "error",
                }
            ]
        }, 404

    if not isinstance(data, dict):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El cuerpo debe ser un objeto JSON",
                    "level": "error",
                }
            ]
        }, 400

    if not data:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El cuerpo no puede estar vacío",
                    "level": "error",
                }
            ]
        }, 400

    campos_permitidos = {
        "nombre",
        "precio_hora",
        "techada",
        "activa",
    }

    campos_desconocidos = (
        set(data.keys())
        - campos_permitidos
    )

    if campos_desconocidos:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Se enviaron campos no editables o desconocidos",
                    "level": "error",
                }
            ]
        }, 400

    fields = []
    params = []

    if "nombre" in data:
        if not isinstance(
            data["nombre"],
            str,
        ):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "nombre debe ser un string",
                        "level": "error",
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
                        "level": "error",
                    }
                ]
            }, 400

        fields.append("nombre = %s")
        params.append(nombre)

    if "precio_hora" in data:
        precio_hora = data[
            "precio_hora"
        ]

        if (
            type(precio_hora) is not int
            or precio_hora <= 0
        ):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "precio_hora debe ser un entero positivo",
                        "level": "error",
                    }
                ]
            }, 400

        fields.append(
            "precio_hora = %s"
        )
        params.append(precio_hora)

    if "techada" in data:
        if type(data["techada"]) is not bool:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "techada debe ser un booleano",
                        "level": "error",
                    }
                ]
            }, 400

        fields.append("techada = %s")
        params.append(
            data["techada"]
        )

    if "activa" in data:
        if type(data["activa"]) is not bool:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "activa debe ser un booleano",
                        "level": "error",
                    }
                ]
            }, 400

        fields.append("activa = %s")
        params.append(
            data["activa"]
        )

    canchas_repository.actualizar(
        cancha_id,
        fields,
        params,
    )

    return obtener_por_id(
        cancha_id
    ), 200


def eliminar_cancha(cancha_id):
    cancha = (
        canchas_repository.obtener_por_id(
            cancha_id
        )
    )

    if not cancha:
        return {
            "errors": [
                {
                    "code": "NOT_FOUND",
                    "message": "Cancha no encontrada",
                    "level": "error",
                }
            ]
        }, 404

    if (
        canchas_repository
        .verificar_reservas_asociadas(
            cancha_id
        )
    ):
        return {
            "errors": [
                {
                    "code": "CONFLICT",
                    "message": "No se puede eliminar una cancha con reservas asociadas",
                    "level": "error",
                }
            ]
        }, 409

    canchas_repository.eliminar(
        cancha_id
    )

    return None, 204


def obtener_canchas_disponibles(
    fecha,
    hora_inicio,
    hora_fin,
    id_deporte=None,
    techada=None,
    limit=10,
    offset=0,
):
    try:
        fecha_obj = datetime.strptime(
            fecha,
            "%Y-%m-%d",
        ).date()

        hora_inicio_obj = (
            datetime.strptime(
                hora_inicio,
                "%H:%M:%S",
            ).time()
        )

        hora_fin_obj = (
            datetime.strptime(
                hora_fin,
                "%H:%M:%S",
            ).time()
        )

    except (ValueError, TypeError):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Fecha u hora con formato inválido",
                    "level": "error",
                }
            ]
        }, 400

    if (
        hora_inicio_obj.minute != 0
        or hora_inicio_obj.second != 0
        or hora_fin_obj.minute != 0
        or hora_fin_obj.second != 0
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Las reservas deben comenzar y terminar en horas en punto",
                    "level": "error",
                }
            ]
        }, 400

    inicio_solicitado = (
        datetime.combine(
            fecha_obj,
            hora_inicio_obj,
        )
    )

    fin_solicitado = (
        datetime.combine(
            fecha_obj,
            hora_fin_obj,
        )
    )

    if (
        inicio_solicitado
        >= fin_solicitado
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "La hora de inicio debe ser menor que la hora de fin",
                    "level": "error",
                }
            ]
        }, 400

    hora_apertura = (
        inicio_solicitado.replace(
            hour=8,
            minute=0,
            second=0,
            microsecond=0,
        )
    )

    hora_cierre = (
        inicio_solicitado.replace(
            hour=23,
            minute=0,
            second=0,
            microsecond=0,
        )
    )

    if (
        inicio_solicitado
        < hora_apertura
        or fin_solicitado
        > hora_cierre
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El intervalo debe estar entre las 08:00 y las 23:00",
                    "level": "error",
                }
            ]
        }, 400

    duracion = (
        fin_solicitado
        - inicio_solicitado
    )

    if (
        duracion < timedelta(hours=1)
        or duracion > timedelta(hours=3)
    ):
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "La duración debe ser de entre 1 y 3 horas",
                    "level": "error",
                }
            ]
        }, 400

    zona_horaria = timezone(
        timedelta(hours=-3)
    )

    ahora = datetime.now(
        zona_horaria
    ).replace(
        tzinfo=None
    )

    if inicio_solicitado <= ahora:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "El inicio debe ser posterior al momento actual",
                    "level": "error",
                }
            ]
        }, 400

    id_deporte_convertido = None

    if id_deporte is not None:
        try:
            id_deporte_convertido = int(
                id_deporte
            )
        except (ValueError, TypeError):
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "id_deporte debe ser un entero",
                        "level": "error",
                    }
                ]
            }, 400

        if id_deporte_convertido <= 0:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "id_deporte debe ser positivo",
                        "level": "error",
                    }
                ]
            }, 400

    techada_convertida = None

    if techada is not None:
        if techada not in [
            "true",
            "false",
        ]:
            return {
                "errors": [
                    {
                        "code": "BAD_REQUEST",
                        "message": "techada debe ser true o false",
                        "level": "error",
                    }
                ]
            }, 400

        techada_convertida = (
            techada == "true"
        )

    canchas, total = (
        canchas_repository
        .obtener_canchas_disponibles(
            inicio_solicitado,
            fin_solicitado,
            id_deporte_convertido,
            techada_convertida,
            limit,
            offset,
        )
    )

    for cancha in canchas:
        cancha["techada"] = bool(
            cancha["techada"]
        )

        cancha["activa"] = bool(
            cancha["activa"]
        )

    extra_params = {
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
    }

    if id_deporte is not None:
        extra_params[
            "id_deporte"
        ] = id_deporte

    if techada is not None:
        extra_params[
            "techada"
        ] = techada

    return {
        "canchas": canchas,
        "total": total,
        "extra_params": extra_params,
    }, 200