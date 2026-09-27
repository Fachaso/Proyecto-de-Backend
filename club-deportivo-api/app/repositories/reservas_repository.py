from datetime import datetime
import app.db as db


CAMPOS_RESERVA = """
    id,
    id_cancha,
    id_socio,
    fecha_hora_inicio,
    fecha_hora_fin,
    tarifa_historica AS tarifa_hora_historica,
    total AS importe_total,
    estado
"""


def obtener_con_filtros(where_sql, params, limit, offset):
    """
    Recupera reservas paginadas aplicando filtros dinámicos.
    Mapea 'tarifa_historica' a 'tarifa_hora_historica' y 'total' a 'importe_total'.
    """
    resultado = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        count_query = f"SELECT COUNT(*) AS total FROM reservas{where_sql}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        data_query = (
            f"SELECT {CAMPOS_RESERVA} "
            f"FROM reservas{where_sql} "
            f"ORDER BY id ASC "
            f"LIMIT %s OFFSET %s"
        )
        cursor.execute(data_query, params + [limit, offset])
        reservas = cursor.fetchall()

        resultado = (reservas, total)
    finally:
        cursor.close()
        conn.close()

    return resultado


def obtener_por_id(reserva_id: int):
    """
    Recupera el detalle completo de una reserva por su clave primaria.
    """
    reserva = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"SELECT {CAMPOS_RESERVA} FROM reservas WHERE id = %s"
        cursor.execute(query, (reserva_id,))
        reserva = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return reserva


def obtener_cancha(id_cancha: int):
    """Recupera cancha por ID para validar existencia, tarifa y estado activo."""
    cancha = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, nombre, precio_hora, activa FROM canchas WHERE id = %s",
            (id_cancha,)
        )
        cancha = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return cancha


def obtener_socio(id_socio: int):
    """Recupera socio por ID para validar existencia y estado activo."""
    socio = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, nombre, email, activo FROM socios WHERE id = %s",
            (id_socio,)
        )
        socio = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return socio


def verificar_superposicion_cancha(id_cancha: int, dt_inicio: datetime, dt_fin: datetime):
    """
    Evalúa colisión horaria en la misma cancha.
    Fórmula oficial: A_inicio < B_fin AND A_fin > B_inicio con estado = 'confirmada'.
    """
    superpuesto = False
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT 1 FROM reservas
            WHERE id_cancha = %s
              AND estado = 'confirmada'
              AND fecha_hora_inicio < %s
              AND fecha_hora_fin > %s
            LIMIT 1
        """
        inicio_str = dt_inicio.strftime("%Y-%m-%d %H:%M:%S")
        fin_str = dt_fin.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (id_cancha, fin_str, inicio_str))
        superpuesto = (cursor.fetchone() is not None)
    finally:
        cursor.close()
        conn.close()

    return superpuesto


def verificar_superposicion_socio(id_socio: int, dt_inicio: datetime, dt_fin: datetime):
    """
    Evalúa colisión horaria en la agenda del socio responsable.
    Impide que un socio tenga reservas confirmadas superpuestas en canchas distintas.
    """
    superpuesto = False
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT 1 FROM reservas
            WHERE id_socio = %s
              AND estado = 'confirmada'
              AND fecha_hora_inicio < %s
              AND fecha_hora_fin > %s
            LIMIT 1
        """
        inicio_str = dt_inicio.strftime("%Y-%m-%d %H:%M:%S")
        fin_str = dt_fin.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (id_socio, fin_str, inicio_str))
        superpuesto = (cursor.fetchone() is not None)
    finally:
        cursor.close()
        conn.close()

    return superpuesto


def crear(id_cancha: int, id_socio: int, dt_inicio: datetime, dt_fin: datetime,
          tarifa_historica: int, total: int):
    """
    Inserta una reserva en estado 'confirmada' congelando tarifa e importe total.
    Aplica el principio de salida única (un único return).
    """
    nuevo_id = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO reservas (
                id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin,
                tarifa_historica, total, estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'confirmada')
        """
        inicio_str = dt_inicio.strftime("%Y-%m-%d %H:%M:%S")
        fin_str = dt_fin.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            query,
            (
                id_cancha,
                id_socio,
                inicio_str,
                fin_str,
                tarifa_historica,
                total,
            ),
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

    return nuevo_id


def actualizar_estado(reserva_id: int, nuevo_estado: str):
    """Actualiza el estado de una reserva en la base de datos."""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE reservas SET estado = %s WHERE id = %s"
        cursor.execute(query, (nuevo_estado, reserva_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return None