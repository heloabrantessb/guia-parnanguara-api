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

    def test_atualizar_perfil_sucesso(self):
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        login_res = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps({"email": "joao@example.com", "senha": "senha123"}),
            content_type="application/json",
        )
        token = login_res.json()["token"]

        update_payload = {
            "nome": "João Silva Alterado",
            "foto_perfil": "https://example.com/foto.jpg",
        }
        response = self.client.put(
            "/v1/usuarios/perfil",
            data=json.dumps(update_payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["nome"], "João Silva Alterado")
        self.assertEqual(data["foto_perfil"], "https://example.com/foto.jpg")

    def test_atualizar_perfil_email_duplicado(self):
        # Cria outro usuário
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps({
                "nome": "Maria",
                "email": "maria@example.com",
                "senha": "senha123"
            }),
            content_type="application/json",
        )
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        login_res = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps({"email": "joao@example.com", "senha": "senha123"}),
            content_type="application/json",
        )
        token = login_res.json()["token"]

        response = self.client.put(
            "/v1/usuarios/perfil",
            data=json.dumps({"email": "maria@example.com"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"error": "Email já cadastrado"})

    def test_atualizar_senha_sucesso_e_erro(self):
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        login_res = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps({"email": "joao@example.com", "senha": "senha123"}),
            content_type="application/json",
        )
        token = login_res.json()["token"]

        # Senha incorreta
        res_err = self.client.put(
            "/v1/usuarios/perfil",
            data=json.dumps({"senha_atual": "errada", "nova_senha": "novasenha123"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(res_err.status_code, 400)
        self.assertEqual(res_err.json(), {"error": "Senha atual incorreta"})

        # Senha correta
        res_ok = self.client.put(
            "/v1/usuarios/perfil",
            data=json.dumps({"senha_atual": "senha123", "nova_senha": "novasenha123"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(res_ok.status_code, 200)

        # Tentar login com nova senha
        login_new = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps({"email": "joao@example.com", "senha": "novasenha123"}),
            content_type="application/json",
        )
        self.assertEqual(login_new.status_code, 200)

    def test_deletar_perfil_soft_delete(self):
        self.client.post(
            "/v1/usuarios/registro",
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        login_res = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps({"email": "joao@example.com", "senha": "senha123"}),
            content_type="application/json",
        )
        token = login_res.json()["token"]

        # Deletar perfil
        delete_res = self.client.delete(
            "/v1/usuarios/perfil",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(delete_res.status_code, 200)
        self.assertEqual(delete_res.json(), {"message": "Conta desativada com sucesso"})

        # Verificar se usuário no banco está com is_active=False e desativado_em preenchido
        user = Usuario.objects.get(email="joao@example.com")
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.desativado_em)

        # Tentativa de login após soft delete deve falhar
        login_fail = self.client.post(
            "/v1/usuarios/login",
            data=json.dumps({"email": "joao@example.com", "senha": "senha123"}),
            content_type="application/json",
        )
        self.assertEqual(login_fail.status_code, 401)

        # Tentativa de acessar perfil com token antigo deve falhar (JWTAuth filtra is_active=True)
        get_profile_fail = self.client.get(
            "/v1/usuarios/perfil",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(get_profile_fail.status_code, 401)

