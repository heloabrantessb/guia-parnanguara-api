import json
from django.test import TestCase
from usuarios.models import Usuario


class UsuarioAPITestCase(TestCase):
    def setUp(self):
        self.user_data = {
            "nome": "João da Silva",
            "email": "joao@example.com",
            "senha": "senha123"
        }

    def test_registro_sucesso(self):
        response = self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "joao@example.com")
        self.assertEqual(data["nome"], "João da Silva")
        self.assertEqual(data["funcao"], "usuario")
        self.assertNotIn("password", data)
        self.assertNotIn("senha", data)

    def test_registro_email_duplicado(self):
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        response = self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"error": "Email já cadastrado"})

    def test_login_sucesso(self):
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        login_payload = {
            "email": "joao@example.com",
            "senha": "senha123"
        }
        response = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps(login_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["usuario"]["email"], "joao@example.com")

    def test_login_credenciais_invalidas(self):
        login_payload = {
            "email": "inexistente@example.com",
            "senha": "errada"
        }
        response = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps(login_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Email ou senha inválidos"})

    def test_perfil_autenticado(self):
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        login_response = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps({
                "email": "joao@example.com",
                "senha": "senha123"
            }),
            content_type="application/json",
        )
        token = login_response.json()["token"]

        response = self.client.get(
            "/v1/usuarios/perfil",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "joao@example.com")

    def test_perfil_sem_token(self):
        response = self.client.get("/v1/usuarios/perfil")
        self.assertEqual(response.status_code, 401)
