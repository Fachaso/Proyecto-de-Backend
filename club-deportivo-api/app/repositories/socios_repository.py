import app.db as db

def obtener_con_filtros(where_sql, params, limit, offset):
    conn = db.get_db_connection()
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

def verificar_email_existente(email, socio_id_excluir=None):
    conn = db.get_db_connection()
    try:
        with conn.cursor() as cursor:
            if socio_id_excluir:
                 query = "SELECT id FROM socios WHERE LOWER(email) = %s AND id != %s"
                 cursor.execute(query, (email.lower(), socio_id_excluir))
            else:
                 query = "SELECT id FROM socios WHERE LOWER(email) = %s"
                 cursor.execute(query, (email.lower(),))
            return cursor.fetchone() is not None 
    finally:
            conn.close()

def crear(nombre, email, activo):
    conn = db.get_db_connection()
    try:
         with conn.cursor() as cursor:
             query = "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, %s)"
             cursor.execute(query, (nombre, email, activo))
             conn.commit()
             return cursor.lastrowid
        finally:
            conn.close()
            
def obtener_por_id(socio_id):
    conn = db.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre, email, activo FROM socios WHERE id = %s", (socio_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def actualizar(socio_id, nombre, email, activo):
    conn = db.get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = "UPDATE socios SET nombre = %s, email = %s, activo = %s WHERE id = %s"
            cursor.execute(query, (nombre, email, activo, socio_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()
            
def tiene_reservas_asociadas(socio_id):
    conn = db.get_db_connection()
    try:
         with conn.cursor() as cursor:
            query = "SELECT id FROM reservas WHERE id_socio = %s AND estado = 'confirmada'"
            cursor.execute(query, (socio_id,))
            return cursor.fetchone() is not None
     finally:
        conn.close()
