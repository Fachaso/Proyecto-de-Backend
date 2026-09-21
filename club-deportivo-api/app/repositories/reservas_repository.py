from app.db import get_db_connection

class ReservasRepository:

    @staticmethod
    def obtener_con_filtros(where_sql, params, limit, offset):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                count_query = f"SELECT COUNT(*) as total FROM reservas{where_sql}"
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                data_query = f"SELECT id, id_cancha, id_socio, fecha, hora_inicio, duracion_horas, precio_total FROM reservas{where_sql} ORDER BY id ASC LIMIT %s OFFSET %s"
                cursor.execute(data_query, params + [limit, offset])
                reservas = cursor.fetchall()
                return reservas, total
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(reserva_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, id_cancha, id_socio, fecha, hora_inicio, duracion_horas, precio_total FROM reservas WHERE id = %s", (reserva_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def obtener_cancha(id_cancha):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, precio_hora, activa FROM canchas WHERE id = %s", (id_cancha,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def obtener_usuario(id_socio):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id_socio,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def verificar_superposicion(id_cancha, fecha, hora_inicio, duracion_horas):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM reservas WHERE id_cancha = %s AND fecha = %s AND "
                    "(hora_inicio < ADDTIME(%s, SEC_TO_TIME(%s * 3600)) AND ADDTIME(hora_inicio, SEC_TO_TIME(duracion_horas * 3600)) > %s)",
                    (id_cancha, fecha, hora_inicio, duracion_horas, hora_inicio)
                )
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def crear(id_cancha, id_socio, fecha, hora_inicio, duracion_horas, precio_total):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "INSERT INTO reservas (id_cancha, id_socio, fecha, hora_inicio, duracion_horas, precio_total) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (id_cancha, id_socio, fecha, hora_inicio, duracion_horas, precio_total))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def actualizar_estado(reserva_id, nuevo_estado):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "UPDATE reservas SET estado = %s WHERE id = %s"
                cursor.execute(query, (nuevo_estado, reserva_id))
                conn.commit()
        finally:
            conn.close()