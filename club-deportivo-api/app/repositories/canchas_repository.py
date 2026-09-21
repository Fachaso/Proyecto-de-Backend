from app.db import get_db_connection

class CanchasRepository:

    @staticmethod
    def obtener_con_filtros(where_sql, params, limit, offset):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                count_query = f"SELECT COUNT(*) as total FROM canchas{where_sql}"
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                data_query = f"SELECT id, id_deporte, nombre, precio_hora, techada, activa FROM canchas{where_sql} ORDER BY id ASC LIMIT %s OFFSET %s"
                cursor.execute(data_query, params + [limit, offset])
                canchas = cursor.fetchall()
                return canchas, total
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(cancha_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, id_deporte, nombre, precio_hora, techada, activa FROM canchas WHERE id = %s", (cancha_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def verificar_deporte(id_deporte):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM deportes WHERE id = %s", (id_deporte,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def verificar_reservas_asociadas(cancha_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM reservas WHERE id_cancha = %s LIMIT 1", (cancha_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def crear(id_deporte, nombre, precio_hora, techada, activa):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "INSERT INTO canchas (id_deporte, nombre, precio_hora, techada, activa) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (id_deporte, nombre, precio_hora, techada, activa))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def actualizar(cancha_id, fields, params):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                params.append(cancha_id)
                cursor.execute(f"UPDATE canchas SET {', '.join(fields)} WHERE id = %s", params)
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def eliminar(cancha_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM canchas WHERE id = %s", (cancha_id,))
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def obtener_canchas_disponibles(fecha, hora_inicio, hora_fin, id_deporte):
        inicio_solicitado = f"{fecha} {hora_inicio}"
        fin_solicitado = f"{fecha} {hora_fin}"
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT c.id, c.id_deporte, c.nombre, c.precio_hora, c.techada, c.activa
                    FROM canchas c
                    WHERE c.activa = 1
                    AND NOT EXISTS (
                        SELECT 1
                        FROM reservas r
                        WHERE r.id_cancha = c.id
                        AND r.estado != 'cancelada' 
                        AND r.fecha_hora_inicio < %s 
                        AND r.fecha_hora_fin > %s
                    )
                """
                
                params = [fin_solicitado, inicio_solicitado]
                
                if id_deporte:
                    query += " AND c.id_deporte = %s"
                    params.append(id_deporte)
                    
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            conn.close()
    @staticmethod
    def verificar_formato_fecha(fecha):
        from datetime import datetime
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    @staticmethod
    def verificar_formato_hora(hora):
        from datetime import datetime
        try:
            datetime.strptime(hora, '%H:%M:%S')
            return True
        except ValueError:
            return False
        