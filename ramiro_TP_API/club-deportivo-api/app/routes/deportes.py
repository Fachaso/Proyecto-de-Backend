from flask import Blueprint, jsonify
from app.db import get_db_connection

deportes_bp = Blueprint('deportes', __name__)

@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC")
            deportes = cursor.fetchall()
        return jsonify(deportes), 200
    finally:
        connection.close()
