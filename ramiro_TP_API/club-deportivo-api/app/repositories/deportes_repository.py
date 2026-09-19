from app.db import get_db_connection

class DeportesRepository:

    @staticmethod
    def obtener_todos():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC")
                return cursor.fetchall()
        finally:
            conn.close()