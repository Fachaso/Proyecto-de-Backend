import unittest
from unittest.mock import patch

from app import create_app


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    @patch("app.routes.deportes.deportes_service.listar_deportes")
    def test_listar_deportes(self, listar_deportes):
        listar_deportes.return_value = (
            {"deportes": [{"id": 1, "nombre": "Fútbol"}]},
            200,
        )

        response = self.client.get("/deportes")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["deportes"][0]["nombre"], "Fútbol")
        listar_deportes.assert_called_once_with()

    @patch("app.routes.deportes.deportes_service.listar_deportes")
    def test_listar_deportes_vacio_devuelve_204(self, listar_deportes):
        listar_deportes.return_value = (None, 204)

        response = self.client.get("/deportes")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")

    @patch("app.routes.socios.SociosService.listar_socios")
    def test_listar_socios_con_filtros_y_paginacion(self, listar_socios):
        listar_socios.return_value = (
            {"socios": [{"id": 2, "nombre": "Ana", "email": "ana@mail.com", "activo": True}]},
            200,
        )

        response = self.client.get("/socios?nombre=ana&activo=true&_limit=5&_offset=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["socios"][0]["id"], 2)
        listar_socios.assert_called_once_with(5, 2, "ana", None, "true")

    @patch("app.routes.socios.SociosService.crear_socio")
    def test_crear_socio_devuelve_location(self, crear_socio):
        crear_socio.return_value = (
            {"id": 7, "nombre": "Ana", "email": "ana@mail.com", "activo": True},
            201,
        )

        response = self.client.post(
            "/socios",
            json={"nombre": "Ana", "email": "ana@mail.com"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["Location"], "/socios/7")
        self.assertEqual(response.data, b"")

    @patch("app.routes.socios.SociosService.obtener_por_id")
    def test_obtener_socio_inexistente(self, obtener_por_id):
        obtener_por_id.return_value = (
            {"errors": [{"code": "NOT_FOUND", "message": "Socio no encontrado"}]},
            404,
        )

        response = self.client.get("/socios/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["errors"][0]["code"], "NOT_FOUND")

    @patch("app.routes.canchas.canchas_service.listar_canchas")
    def test_listar_canchas_incluye_links_de_paginacion(self, listar_canchas):
        listar_canchas.return_value = (
            [{"id": 1, "nombre": "Cancha 1", "techada": True, "activa": True}],
            3,
            {"id_deporte": "1"},
        )

        response = self.client.get("/canchas?id_deporte=1&_limit=2&_offset=0")

        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["canchas"][0]["nombre"], "Cancha 1")
        self.assertEqual(body["_links"]["_next"], "/canchas?id_deporte=1&_limit=2&_offset=2")
        listar_canchas.assert_called_once_with(2, 0, "1", None, None, None)

    def test_consultar_disponibilidad_sin_parametros_requeridos(self):
        response = self.client.get("/canchas/disponibles?fecha=2030-01-01")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["errors"][0]["code"], "ERROR_VALIDACION")

    @patch("app.routes.canchas.canchas_service.obtener_canchas_disponibles")
    def test_consultar_canchas_disponibles(self, disponibles):
        disponibles.return_value = (
            {
                "canchas": [{"id": 1, "nombre": "Cancha 1"}],
                "total": 1,
                "extra_params": {"fecha": "2030-01-01"},
            },
            200,
        )

        response = self.client.get(
            "/canchas/disponibles?fecha=2030-01-01&hora_inicio=10:00:00&hora_fin=11:00:00"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["canchas"][0]["id"], 1)
        disponibles.assert_called_once_with(
            "2030-01-01", "10:00:00", "11:00:00", None, None, 10, 0
        )

    @patch("app.routes.canchas.canchas_service.crear_cancha")
    def test_crear_cancha_devuelve_201_y_location(self, crear_cancha):
        crear_cancha.return_value = (
            {"id": 4, "id_deporte": 1, "nombre": "Cancha nueva", "precio_hora": 5000},
            201,
        )
        payload = {"id_deporte": 1, "nombre": "Cancha nueva", "precio_hora": 5000}

        response = self.client.post("/canchas", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["Location"], "/canchas/4")
        crear_cancha.assert_called_once_with(payload)

    @patch("app.routes.canchas.canchas_service.eliminar_cancha")
    def test_eliminar_cancha_sin_reservas(self, eliminar_cancha):
        eliminar_cancha.return_value = (None, 204)

        response = self.client.delete("/canchas/4")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")
        eliminar_cancha.assert_called_once_with(4)

    @patch("app.routes.reservas.listar_reservas")
    def test_listar_reservas_vacio(self, listar_reservas):
        listar_reservas.return_value = (None, 204)

        response = self.client.get("/reservas?id_cancha=1&fecha=2030-01-01")

        self.assertEqual(response.status_code, 204)
        listar_reservas.assert_called_once_with(10, 0, "1", "2030-01-01")

    @patch("app.routes.reservas.crear_reserva")
    def test_crear_reserva_devuelve_location(self, crear_reserva):
        crear_reserva.return_value = (
            {"id": 9, "id_cancha": 1, "id_socio": 2, "precio_total": 10000},
            201,
        )
        payload = {
            "id_cancha": 1,
            "id_socio": 2,
            "fecha": "2030-01-01",
            "hora_inicio": "10:00",
            "duracion_horas": 2,
        }

        response = self.client.post("/reservas", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["Location"], "/reservas/9")
        crear_reserva.assert_called_once_with(payload)

    def test_actualizar_estado_sin_estado_es_invalido(self):
        response = self.client.put("/reservas/9/estado", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["errors"][0]["code"], "ERROR_VALIDACION")

    @patch("app.routes.reservas.actualizar_estado")
    def test_actualizar_estado_de_reserva(self, actualizar_estado):
        actualizar_estado.return_value = (
            {"mensaje": "Estado de la reserva actualizado correctamente"},
            200,
        )

        response = self.client.put("/reservas/9/estado", json={"estado": "cancelada"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["mensaje"],
            "Estado de la reserva actualizado correctamente",
        )
        actualizar_estado.assert_called_once_with(9, "cancelada")


if __name__ == "__main__":
    unittest.main()
