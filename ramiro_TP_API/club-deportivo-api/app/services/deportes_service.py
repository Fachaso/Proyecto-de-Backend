from app.repositories.deportes_repository import DeportesRepository

class DeportesService:

    @staticmethod
    def listar_deportes():
        # Aquí podrías agregar lógica de negocio si la hubiera en el futuro
        return DeportesRepository.obtener_todos()