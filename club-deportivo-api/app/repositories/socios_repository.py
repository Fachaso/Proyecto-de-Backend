import app.db as db

import app.db as db

def obtener_por_id(reserva_id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_total
            FROM reservas
            WHERE id = %s
            """,
            (reserva_id,),
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def crear(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_total):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO reservas (
                id_socio,
                id_cancha,
                fecha_hora_inicio,
                fecha_hora_fin,
                estado,
                precio_total
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                id_socio,
                id_cancha,
                fecha_hora_inicio,
                fecha_hora_fin,
                estado,
                precio_total,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        conn.close()


def actualizar_estado(reserva_id, nuevo_estado):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE reservas
            SET estado = %s
            WHERE id = %s
        """
        cursor.execute(query, (nuevo_estado, reserva_id))
        conn.commit()

    finally:
        cursor.close()
        conn.close()


def obtener_con_filtros(where_sql, params, limit, offset):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        count_query = (
            f"SELECT COUNT(*) AS total "
            f"FROM reservas{where_sql}"
        )
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        data_query = (
            f"SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_total "
            f"FROM reservas{where_sql} "
            f"ORDER BY id ASC "
            f"LIMIT %s OFFSET %s"
        )

        cursor.execute(
            data_query,
            params + [limit, offset],
        )

        reservas = cursor.fetchall()

        return reservas, total

    finally:
        cursor.close()
        conn.close()