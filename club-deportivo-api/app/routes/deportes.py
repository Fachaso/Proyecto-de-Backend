from flask import Blueprint, jsonify
from app.services.deportes_service import DeportesService

deportes_bp = Blueprint('deportes', __name__, url_prefix='/deportes')

@deportes_bp.route('', methods=['GET'])
def get_deportes():
    respuesta, estado = DeportesService.listar_deportes()
    
    if estado == 204:
        return '', 204
        
    return jsonify(respuesta), estado