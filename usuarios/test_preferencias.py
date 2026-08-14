import json
from django.test import TestCase
from usuarios.models import Usuario
from usuarios.auth import generate_token
from atrativos.models import Categoria

class PreferenciasAPITestCase(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="user_pref@example.com",
            email="user_pref@example.com",
            nome="User Preferencias",
            password="password123"
        )
        self.token = generate_token(self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.cat1 = Categoria.objects.create(titulo="Praia", tipo="local")
        self.cat2 = Categoria.objects.create(titulo="Gastronomia", tipo="ambos")

    def test_listar_preferencias_vazio(self):
        response = self.client.get("/v1/preferencias/", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_definir_preferencias_sucesso(self):
        payload = {"categoria_ids": [self.cat1.id, self.cat2.id]}
        response = self.client.post(
            "/v1/preferencias/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_definir_preferencias_categoria_inexistente(self):
        payload = {"categoria_ids": [self.cat1.id, 9999]}
        response = self.client.post(
            "/v1/preferencias/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_deletar_preferencia_sucesso(self):
        self.user.preferencias.add(self.cat1)
        
        response = self.client.delete(f"/v1/preferencias/{self.cat1.id}", **self.headers)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.user.preferencias.filter(id=self.cat1.id).exists())

    def test_deletar_preferencia_nao_cadastrada(self):
        response = self.client.delete(f"/v1/preferencias/{self.cat2.id}", **self.headers)
        self.assertEqual(response.status_code, 404)
