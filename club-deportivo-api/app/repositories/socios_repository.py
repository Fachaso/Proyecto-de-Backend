from app.db import get_db_connection

class SociosRepository:
    
    @staticmethod
    def obtener_con_filtros(where_sql, params, limit, offset):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                count_query = f"SELECT COUNT(*) as total FROM socios{where_sql}"
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                data_query = f"SELECT id, nombre, email, activo FROM socios{where_sql} ORDER BY id ASC LIMIT %s OFFSET %s"
                cursor.execute(data_query, params + [limit, offset])
                socios = cursor.fetchall()
                return socios, total
        finally:
            conn.close()

    @staticmethod
    def verificar_email_existente(email):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM socios WHERE LOWER(email) = %s", (email.lower(),))
                return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def crear(nombre, email, activo):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, %s)"
                cursor.execute(query, (nombre, email, activo))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(socio_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre, email, activo FROM socios WHERE id = %s", (socio_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def actualizar(socio_id, nombre, email, activo):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "UPDATE socios SET nombre = %s, email = %s, activo = %s WHERE id = %s"
                cursor.execute(query, (nombre, email, activo, socio_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()