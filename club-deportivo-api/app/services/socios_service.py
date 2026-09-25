import app.repositories.socios_repository as socios_repository

def listar_socios(limit, offset, nombre, email, activo):
    where_clauses = []
    params = []
    extra_params = {}

    if nombre:
        where_clauses.append("LOWER(nombre) LIKE %s")
        params.append(f"%{nombre.lower()}%")
        extra_params['nombre'] = nombre

    if email:
        where_clauses.append("LOWER(email) LIKE %s")
        params.append(f"%{email.lower()}%")
        extra_params['email'] = email

    if activo in ['true', 'false']:
        where_clauses.append("activo = %s")
        params.append(1 if activo == 'true' else 0)
        extra_params['activo'] = activo

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    socios, total = socios_repository.obtener_con_filtros(where_sql, params, limit, offset)

    if not socios:
        return None, 204

    for s in socios:
        s['activo'] = bool(s['activo'])

    return {"socios": socios}, 200

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
    nombre = str(data.get('nombre', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    activo = bool(data.get('activo', True))

    if not nombre or not email:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Campos obligatorios faltantes",
                    "level": "error"
                }
            ]
        }, 400

    if socios_repository.verificar_email_existente(email):
        return {
            "errors": [
                {
                    "code": "CONFLICT",
                    "message": "El correo electrónico ya se encuentra registrado",
                    "level": "error"
                }
            ]
        }, 409

    socio_id = socios_repository.crear(nombre, email, activo)
    return {'id': socio_id, 'nombre': nombre, 'email': email, 'activo': activo}, 201

def actualizar_socio(socio_id, data):
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

    nombre = str(data.get('nombre', socio['nombre'])).strip()
    email = str(data.get('email', socio['email'])).strip().lower()
    activo = bool(data.get('activo', socio['activo']))

    if not nombre or not email:
        return {
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": "Campos obligatorios faltantes",
                    "level": "error"
                }
            ]
        }, 400

    if email != socio['email'].lower() and socios_repository.verificar_email_existente(email):
        return {
            "errors": [
                {
                    "code": "CONFLICT",
                    "message": "El correo electrónico ya se encuentra registrado",
                    "level": "error"
                }
            ]
        }, 409

    socios_repository.actualizar(socio_id, nombre, email, activo)
    return {'id': socio_id, 'nombre': nombre, 'email': email, 'activo': activo}, 200
