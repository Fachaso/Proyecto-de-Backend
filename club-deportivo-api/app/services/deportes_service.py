from app.repositories.deportes_repository import obtener_todos


def listar_deportes():
    deportes = obtener_todos()

    if not deportes:
        return None, 204

    return {"deportes": deportes}, 200
