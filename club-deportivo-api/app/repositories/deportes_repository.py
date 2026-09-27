import app.db as db


def obtener_todos():
    """
    Recupera todos los deportes precargados ordenados por ID ascendente.
    """
    deportes = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC")
        deportes = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return deportes


def obtener_por_id(deporte_id: int):
    """
    Recupera un deporte por su clave primaria.
    Utilizado por otros módulos para verificar la existencia del deporte (FK).
    """
    deporte = None
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, nombre FROM deportes WHERE id = %s",
            (deporte_id,)
        )
        deporte = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return deporte