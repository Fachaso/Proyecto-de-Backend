import app.db as db


def obtener_con_filtros(where_sql, params, limit, offset):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            count_query = (
                f"SELECT COUNT(*) AS total "
                f"FROM canchas{where_sql}"
            )
            cursor.execute(count_query, params)
            total = cursor.fetchone()["total"]

            data_query = (
                f"SELECT id, id_deporte, nombre, precio_hora, techada, activa "
                f"FROM canchas{where_sql} "
                f"ORDER BY id ASC "
                f"LIMIT %s OFFSET %s"
            )

            cursor.execute(
                data_query,
                params + [limit, offset],
            )

            canchas = cursor.fetchall()

            return canchas, total

    finally:
        conn.close()


def obtener_por_id(cancha_id):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, id_deporte, nombre, precio_hora, techada, activa
                FROM canchas
                WHERE id = %s
                """,
                (cancha_id,),
            )

            return cursor.fetchone()

    finally:
        conn.close()


def verificar_deporte(id_deporte):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM deportes
                WHERE id = %s
                """,
                (id_deporte,),
            )

            return cursor.fetchone()

    finally:
        conn.close()


def verificar_reservas_asociadas(cancha_id):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM reservas
                WHERE id_cancha = %s
                LIMIT 1
                """,
                (cancha_id,),
            )

            return cursor.fetchone() is not None

    finally:
        conn.close()


def crear(id_deporte, nombre, precio_hora, techada, activa):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO canchas (
                    id_deporte,
                    nombre,
                    precio_hora,
                    techada,
                    activa
                )
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    id_deporte,
                    nombre,
                    precio_hora,
                    techada,
                    activa,
                ),
            )

            conn.commit()

            return cursor.lastrowid

    finally:
        conn.close()


def actualizar(cancha_id, fields, params):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            query = (
                f"UPDATE canchas "
                f"SET {', '.join(fields)} "
                f"WHERE id = %s"
            )

            cursor.execute(
                query,
                params + [cancha_id],
            )

            conn.commit()

    finally:
        conn.close()


def eliminar(cancha_id):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM canchas
                WHERE id = %s
                """,
                (cancha_id,),
            )

            conn.commit()

    finally:
        conn.close()


def obtener_canchas_disponibles(
    inicio_solicitado,
    fin_solicitado,
    id_deporte=None,
    techada=None,
    limit=10,
    offset=0,
):
    conn = db.get_db_connection()

    try:
        with conn.cursor() as cursor:
            where_clauses = [
                "c.activa = TRUE",
                """
                NOT EXISTS (
                    SELECT 1
                    FROM reservas r
                    WHERE r.id_cancha = c.id
                    AND r.estado = 'confirmada'
                    AND r.fecha_hora_inicio < %s
                    AND r.fecha_hora_fin > %s
                )
                """,
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
                params.append(techada)

            where_sql = (
                " WHERE "
                + " AND ".join(where_clauses)
            )

            count_query = (
                f"SELECT COUNT(*) AS total "
                f"FROM canchas c"
                f"{where_sql}"
            )

            cursor.execute(
                count_query,
                params,
            )

            total = cursor.fetchone()["total"]

            data_query = (
                f"SELECT "
                f"c.id, "
                f"c.id_deporte, "
                f"c.nombre, "
                f"c.precio_hora, "
                f"c.techada, "
                f"c.activa "
                f"FROM canchas c"
                f"{where_sql} "
                f"ORDER BY c.id ASC "
                f"LIMIT %s OFFSET %s"
            )

            cursor.execute(
                data_query,
                params + [limit, offset],
            )

            canchas = cursor.fetchall()

            return canchas, total

    finally:
        conn.close()