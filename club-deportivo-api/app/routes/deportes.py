from flask import Blueprint, jsonify
from app.services.deportes_service import DeportesService

deportes_bp = Blueprint('deportes', __name__)

@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    deportes = DeportesService.listar_deportes()
    return jsonify(deportes), 200
