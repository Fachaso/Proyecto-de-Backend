import app.repositories.deportes_repository as deportes_repository


def listar_deportes():
    """
    Retorna la lista de deportes precargados.
    Las consultas exitosas devuelven siempre 200 OK con un arreglo.
    """
    deportes = deportes_repository.obtener_todos()
    resultado = deportes if deportes is not None else []
    status = 200

    return resultado, status