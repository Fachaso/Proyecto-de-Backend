import app.db as db


def obtener_con_filtros(where_sql, params, limit, offset):
    """Recupera canchas con filtros dinámicos y total para paginación."""
    resultado = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        count_query = f"SELECT COUNT(1) AS total FROM canchas{where_sql}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        data_query = (
            f"SELECT id, id_deporte, nombre, precio_hora, techada, activa "
            f"FROM canchas{where_sql} "
            f"ORDER BY id ASC "
            f"LIMIT %s OFFSET %s"
        )
        cursor.execute(data_query, params + [limit, offset])
        canchas = cursor.fetchall()
        resultado = (canchas, total)
    finally:
        cursor.close()
        conn.close()

    return resultado


def obtener_por_id(cancha_id):
    """Recupera cancha por ID."""
    cancha = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, id_deporte, nombre, precio_hora, techada, activa
            FROM canchas
            WHERE id = %s
            """,
            (cancha_id,),
        )
        cancha = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return cancha


def verificar_deporte(id_deporte):
    """Comprueba existencia del deporte (FK)."""
    deporte = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM deportes WHERE id = %s", (id_deporte,))
        deporte = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return deporte


def verificar_reservas_asociadas(cancha_id):
    """Verifica si la cancha tiene reservas en cualquier estado."""
    tiene_reservas = False
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM reservas WHERE id_cancha = %s LIMIT 1", (cancha_id,))
        tiene_reservas = (cursor.fetchone() is not None)
    finally:
        cursor.close()
        conn.close()

    return tiene_reservas


def crear(id_deporte, nombre, precio_hora, techada, activa):
    """Inserta una nueva cancha."""
    nuevo_id = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO canchas (id_deporte, nombre, precio_hora, techada, activa)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                id_deporte,
                nombre,
                precio_hora,
                1 if techada else 0,
                1 if activa else 0,
            ),
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

    return nuevo_id


def actualizar(cancha_id, fields, params):
    """Actualiza dinámicamente columnas de la cancha."""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"UPDATE canchas SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, params + [cancha_id])
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return None


def eliminar(cancha_id):
    """Eliminación física de la cancha."""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM canchas WHERE id = %s", (cancha_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return None


def obtener_canchas_disponibles(
    inicio_solicitado,
    fin_solicitado,
    id_deporte=None,
    techada=None,
    limit=10,
    offset=0,
):
    """
    Consulta canchas activas sin turnos confirmados superpuestos en el intervalo.
    """
    resultado = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        where_clauses = [
            "c.activa = 1",
            """NOT EXISTS (
                SELECT 1
                FROM reservas r
                WHERE r.id_cancha = c.id
                AND r.estado = 'confirmada'
                AND r.fecha_hora_inicio < %s
                AND r.fecha_hora_fin > %s
            )""",
        ]

        params = [
            fin_solicitado,
            inicio_solicitado,
        ]

        if id_deporte is not None:
            where_clauses.append("c.id_deporte = %s")
            params.append(id_deporte)

        if techada is not None:
            where_clauses.append("c.techada = %s")
            params.append(1 if techada else 0)

        where_sql = " WHERE " + " AND ".join(where_clauses)

        count_query = f"SELECT COUNT(1) AS total FROM canchas c{where_sql}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        data_query = (
            f"SELECT c.id, c.id_deporte, c.nombre, c.precio_hora, c.techada, c.activa "
            f"FROM canchas c{where_sql} "
            f"ORDER BY c.id ASC "
            f"LIMIT %s OFFSET %s"
        )

        cursor.execute(data_query, params + [limit, offset])
        canchas = cursor.fetchall()

        resultado = (canchas, total)
    finally:
        cursor.close()
        conn.close()

    return resultado