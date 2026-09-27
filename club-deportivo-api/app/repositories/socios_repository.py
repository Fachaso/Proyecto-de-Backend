import app.db as db


def obtener_con_filtros(where_sql, params, limit, offset):
    """Recupera socios paginados y el total de coincidencias."""
    resultado = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        count_query = f"SELECT COUNT(*) AS total FROM socios{where_sql}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        data_query = (
            f"SELECT id, nombre, email, activo "
            f"FROM socios{where_sql} "
            f"ORDER BY id ASC "
            f"LIMIT %s OFFSET %s"
        )
        cursor.execute(data_query, params + [limit, offset])
        socios = cursor.fetchall()

        resultado = (socios, total)
    finally:
        cursor.close()
        conn.close()

    return resultado


def obtener_por_id(socio_id):
    """Recupera un socio por su clave primaria."""
    socio = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, nombre, email, activo
            FROM socios
            WHERE id = %s
            """,
            (socio_id,),
        )
        socio = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return socio


def verificar_email_existente(email, socio_id_excluir=None):
    """
    Comprueba si el correo ya está registrado.
    Produce 409 incluso si el socio existente está inactivo.
    """
    existe = False
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        if socio_id_excluir:
            query = "SELECT id FROM socios WHERE LOWER(email) = %s AND id != %s LIMIT 1"
            cursor.execute(query, (email.lower(), socio_id_excluir))
        else:
            query = "SELECT id FROM socios WHERE LOWER(email) = %s LIMIT 1"
            cursor.execute(query, (email.lower(),))

        existe = (cursor.fetchone() is not None)
    finally:
        cursor.close()
        conn.close()

    return existe


def crear(nombre, email, activo=True):
    """Inserta un socio nuevo y retorna el identificador autogenerado."""
    nuevo_id = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO socios (nombre, email, activo)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (nombre, email, 1 if activo else 0))
        conn.commit()
        nuevo_id = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

    return nuevo_id


def actualizar(socio_id, fields, params):
    """Actualiza dinámicamente las columnas indicadas."""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"UPDATE socios SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, params + [socio_id])
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return None