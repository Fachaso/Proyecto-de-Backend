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
    def obtener_canchas_disponibles(inicio_solicitado. fin_solicitado, id_deporte=None, techada=None, limit=10, offset=0):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
               where_clauses = [ 
                   "c.activada = TRUE", 
                   "NOT EXISTS ("
                   "  SELECT 1 FROM reservas r "
                   "  WHERE r.id_cancha = c.id "
                   "  AND r.estado = 'confirmada' "
                   "  AND r.fecha_hora_inicio < %s "
                   "  AND r.fecha_hora_fin > %S"
                   ")"
               ]
               params = [fin_solicitado, inicio_solicitado]
                
                if id_deporte is not None:
                    where_clauses.append("c.id_deporte = %s")
                    params.append(id_deporte)

                if techada is not None:
                    where_clauses.append("c.techada = &S")
                    params.append(techada)

                where_sql = " WHERE " + " AND ".join(where_clauses)
                
                cursor.execute(f"SELECT COUNT(*) as total FROM canchas c{where_sql}", params)
                total = cursor.fetchone()['total']

                query = (
                    f"SELECT c.id, c.id_deporte, c.nombre, c.precio_hora, c.techada, c.activada "
                    f"FROM canchas c{where_sql} ORDER BY c.id ASC LIMIT %s OFFSET %s"
                )
                cursor.execute(query, params + [limit, offset])
                canchas = cursor.fetchall()
                
                return canchas, total
        finally:
            conn.close()
   
