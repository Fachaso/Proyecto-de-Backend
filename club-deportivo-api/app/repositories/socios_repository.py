import app.db as db


def obtener_con_filtros(
    where_sql,
    params,
    limit,
    offset,
):
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        count_query = (
            "SELECT COUNT(*) AS total "
            f"FROM socios{where_sql}"
        )

        cursor.execute(
            count_query,
            params,
        )

        total = cursor.fetchone()["total"]

        data_query = (
            "SELECT id, nombre, email, activo "
            f"FROM socios{where_sql} "
            "ORDER BY id ASC "
            "LIMIT %s OFFSET %s"
        )

        cursor.execute(
            data_query,
            params + [limit, offset],
        )

        socios = cursor.fetchall()

        return socios, total

    finally:
        cursor.close()
        conn.close()


def obtener_por_id(socio_id):
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

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def verificar_email_existente(email):
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id
            FROM socios
            WHERE email = %s
            """,
            (email,),
        )

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def crear(
    nombre,
    email,
    activo,
):
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO socios (
                nombre,
                email,
                activo
            )
            VALUES (%s, %s, %s)
            """,
            (
                nombre,
                email,
                activo,
            ),
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        conn.close()


def actualizar(
    socio_id,
    nombre,
    email,
    activo,
):
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE socios
            SET nombre = %s,
                email = %s,
                activo = %s
            WHERE id = %s
            """,
            (
                nombre,
                email,
                activo,
                socio_id,
            ),
        )

        conn.commit()

    finally:
        cursor.close()
        conn.close()