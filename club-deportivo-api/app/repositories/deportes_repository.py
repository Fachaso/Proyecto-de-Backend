from app.db import get_db_connection


def obtener_todos():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, nombre FROM deportes ORDER BY id ASC"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def obtener_por_id(deporte_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, nombre FROM deportes WHERE id = %s",
            (deporte_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
