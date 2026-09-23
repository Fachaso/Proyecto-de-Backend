from app.repositories.deportes_repository import DeportesRepository

class DeportesService:

    @staticmethod
    def listar_deportes():
        deportes = DeportesRepository.obtener_todos()
        
        # 1. Si no hay deportes guardados, se responde con status 204
        if not deportes:
            return None, 204

        # 2. Si hay deportes, se devuelven envueltos en el objeto {"deportes": [...]} con status 200
        return {"deportes": deportes}, 200