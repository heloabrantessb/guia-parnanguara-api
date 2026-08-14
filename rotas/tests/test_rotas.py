import json
from django.test import TestCase
from usuarios.models import Usuario
from usuarios.auth import generate_token
from atrativos.models import Atrativo
from rotas.models import Rota, RotaAtrativo

class RotasAPITestCase(TestCase):
    def setUp(self):
        self.user1 = Usuario.objects.create_user(
            username="user1@example.com",
            email="user1@example.com",
            nome="User One",
            password="password123"
        )
        self.token1 = generate_token(self.user1)
        self.auth_headers1 = {"HTTP_AUTHORIZATION": f"Bearer {self.token1}"}

        self.user2 = Usuario.objects.create_user(
            username="user2@example.com",
            email="user2@example.com",
            nome="User Two",
            password="password123"
        )
        self.token2 = generate_token(self.user2)
        self.auth_headers2 = {"HTTP_AUTHORIZATION": f"Bearer {self.token2}"}

        self.atrativo1 = Atrativo.objects.create(
            nome="Centro Histórico",
            descricao="Centro histórico de Paranaguá",
            endereco="Rua da Praia",
            latitude="-25.520",
            longitude="-48.508",
        )
        self.atrativo2 = Atrativo.objects.create(
            nome="Santuário do Rocio",
            descricao="Santuário estadual",
            endereco="Bairro do Rocio",
            latitude="-25.530",
            longitude="-48.518",
        )

    def test_criar_rota(self):
        response = self.client.post(
            "/v1/rotas/",
            data=json.dumps({"titulo": "Roteiro Histórico"}),
            content_type="application/json",
            **self.auth_headers1
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["titulo"], "Roteiro Histórico")

    def test_listar_rotas_somente_do_usuario(self):
        Rota.objects.create(usuario=self.user1, titulo="Rota User 1")
        Rota.objects.create(usuario=self.user2, titulo="Rota User 2")

        response = self.client.get("/v1/rotas/", **self.auth_headers1)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["titulo"], "Rota User 1")

    def test_bloqueio_acesso_rota_outro_usuario(self):
        rota_user2 = Rota.objects.create(usuario=self.user2, titulo="Rota Secreta")

        response = self.client.get(f"/v1/rotas/{rota_user2.id}", **self.auth_headers1)
        self.assertEqual(response.status_code, 403)

    def test_adicionar_e_reordenar_atrativo(self):
        rota = Rota.objects.create(usuario=self.user1, titulo="Minha Viagem")

        # Adiciona atrativo 1 na ordem 1
        res1 = self.client.post(
            f"/v1/rotas/{rota.id}/atrativos",
            data=json.dumps({"atrativo_id": self.atrativo1.id, "ordem": 1}),
            content_type="application/json",
            **self.auth_headers1
        )
        self.assertEqual(res1.status_code, 201)

        # Adiciona atrativo 2 na ordem 2
        res2 = self.client.post(
            f"/v1/rotas/{rota.id}/atrativos",
            data=json.dumps({"atrativo_id": self.atrativo2.id, "ordem": 2}),
            content_type="application/json",
            **self.auth_headers1
        )
        self.assertEqual(res2.status_code, 201)

        # Tentar adicionar atrativo duplicado deve retornar 400
        res_dup = self.client.post(
            f"/v1/rotas/{rota.id}/atrativos",
            data=json.dumps({"atrativo_id": self.atrativo1.id, "ordem": 3}),
            content_type="application/json",
            **self.auth_headers1
        )
        self.assertEqual(res_dup.status_code, 400)

        # Remover primeiro atrativo e verificar reordenação
        res_del = self.client.delete(
            f"/v1/rotas/{rota.id}/atrativos/{self.atrativo1.id}",
            **self.auth_headers1
        )
        self.assertEqual(res_del.status_code, 200)
        
        # O segundo atrativo agora deve ser a ordem 1
        item_restante = RotaAtrativo.objects.get(rota=rota)
        self.assertEqual(item_restante.atrativo, self.atrativo2)
        self.assertEqual(item_restante.ordem, 1)
