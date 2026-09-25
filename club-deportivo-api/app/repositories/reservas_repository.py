from app.db import get_db_connection


CAMPOS_RESERVA = """
    id,
    id_cancha,
    id_socio,
    DATE_FORMAT(fecha_hora_inicio, '%Y-%m-%d') AS fecha,
    DATE_FORMAT(fecha_hora_inicio, '%H:%i') AS hora_inicio,
    DATE_FORMAT(fecha_hora_fin, '%H:%i') AS hora_fin,
    estado,
    tarifa_historica,
    total AS precio_total
"""


def obtener_con_filtros(where_sql, params, limit, offset):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"SELECT COUNT(*) AS total FROM reservas{where_sql}",
            params,
        )
        total = cursor.fetchone()["total"]

        consulta = (
            f"SELECT {CAMPOS_RESERVA} "
            f"FROM reservas{where_sql} "
            "ORDER BY id ASC LIMIT %s OFFSET %s"
        )
        cursor.execute(consulta, params + [limit, offset])

        reservas = cursor.fetchall()
        return reservas, total
    finally:
        cursor.close()
        conn.close()


def obtener_por_id(reserva_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"SELECT {CAMPOS_RESERVA} "
            "FROM reservas WHERE id = %s",
            (reserva_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def obtener_cancha(id_cancha):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, precio_hora, activa "
            "FROM canchas WHERE id = %s",
            (id_cancha,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def obtener_socio(id_socio):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, activo FROM socios WHERE id = %s",
            (id_socio,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def verificar_superposicion(id_cancha, fecha_hora_inicio, fecha_hora_fin):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM reservas "
            "WHERE id_cancha = %s "
            "AND estado = 'confirmada' "
            "AND fecha_hora_inicio < %s "
            "AND fecha_hora_fin > %s "
            "LIMIT 1",
            (id_cancha, fecha_hora_fin, fecha_hora_inicio),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def crear(
    id_cancha,
    id_socio,
    fecha_hora_inicio,
    fecha_hora_fin,
    tarifa_historica,
    total,
):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO reservas ("
            "id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, "
            "tarifa_historica, total"
            ") VALUES (%s, %s, %s, %s, %s, %s)",
            (
                id_cancha,
                id_socio,
                fecha_hora_inicio,
                fecha_hora_fin,
                tarifa_historica,
                total,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def actualizar_estado(reserva_id, nuevo_estado):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE reservas SET estado = %s WHERE id = %s",
            (nuevo_estado, reserva_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
