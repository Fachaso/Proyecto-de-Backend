from app.repositories.socios_repository import SociosRepository

class SociosService:
    
    @staticmethod
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

        socios, total = SociosRepository.obtener_con_filtros(where_sql, params, limit, offset)

        for s in socios:
            s['activo'] = bool(s['activo'])

        return socios, total, extra_params
    @staticmethod
    def crear_socio(data):
        nombre = str(data.get('nombre', '')).strip()
        email = str(data.get('email', '')).strip()
        activo = bool(data.get('activo', True))

        if not nombre or not email:
            return {'error': 'Campos obligatorios faltantes'}, 400

        
        if SociosRepository.verificar_email_existente(email):
            return {'error': 'El email ya está registrado'}, 400

        socio_id = SociosRepository.crear(nombre, email, activo)
        return {'id': socio_id, 'nombre': nombre, 'email': email, 'activo': activo}, 201

    @staticmethod
    def obtener_por_id(socio_id):
        socio = SociosRepository.obtener_por_id(socio_id)
        if not socio:
            return None
        socio['activo'] = bool(socio['activo'])
        return socio

    @staticmethod
    def actualizar_socio(socio_id, data):
        socio = SociosRepository.obtener_por_id(socio_id)
        if not socio:
            return {'error': 'Socio no encontrado'}, 404

        nombre = str(data.get('nombre', socio['nombre'])).strip()
        email = str(data.get('email', socio['email'])).strip()
        activo = bool(data.get('activo', socio['activo']))

        if not nombre or not email:
            return {'error': 'Campos obligatorios faltantes'}, 400

        if email.lower() != socio['email'].lower() and SociosRepository.verificar_email_existente(email):
            return {'error': 'El email ya está registrado'}, 400
        SociosRepository.actualizar(socio_id, nombre, email, activo)
        return {'id': socio_id, 'nombre': nombre, 'email': email, 'activo': activo}, 200
