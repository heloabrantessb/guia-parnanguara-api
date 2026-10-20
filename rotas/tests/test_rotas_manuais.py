import json
from unittest.mock import patch

from django.test import TestCase

from atrativos.models import Atrativo
from rotas.models import Rota, RotaAtrativo
from usuarios.auth import generate_token
from usuarios.models import Usuario


class RotasManuaisAPITestCase(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="roteiros@example.com", email="roteiros@example.com",
            nome="Maria", password="senha-de-teste",
        )
        self.cabecalhos = {"HTTP_AUTHORIZATION": f"Bearer {generate_token(self.usuario)}"}
        self.primeiroAtrativo = Atrativo.objects.create(
            nome="Museu", descricao="Museu histórico", endereco="Centro",
            latitude="-25.52", longitude="-48.50",
        )
        self.segundoAtrativo = Atrativo.objects.create(
            nome="Praça", descricao="Praça histórica", endereco="Centro",
            latitude="-25.53", longitude="-48.51",
        )

    def criarRoteiro(self, corpo, cabecalhos=None):
        return self.client.post(
            "/v1/rotas/", data=json.dumps(corpo), content_type="application/json",
            **(self.cabecalhos if cabecalhos is None else cabecalhos),
        )

    def test_preservar_ordem_e_proprietario(self):
        ids = [self.segundoAtrativo.id, self.primeiroAtrativo.id]
        resposta = self.criarRoteiro({"titulo": "  Passeio  ", "atrativo_ids": ids, "usuario_id": 999})
        self.assertEqual(resposta.status_code, 201)
        roteiro = resposta.json()
        self.assertEqual(roteiro["titulo"], "Passeio")
        self.assertEqual([item["atrativo"]["id"] for item in roteiro["itens"]], ids)
        self.assertEqual([item["ordem"] for item in roteiro["itens"]], [1, 2])
        self.assertEqual(Rota.objects.get(id=roteiro["id"]).usuario_id, self.usuario.id)

    def test_exigir_autenticacao(self):
        resposta = self.criarRoteiro({"titulo": "Passeio", "atrativo_ids": [self.primeiroAtrativo.id]}, {})
        self.assertEqual(resposta.status_code, 401)
        self.assertFalse(Rota.objects.exists())

    def test_rejeitar_listas_invalidas_sem_criar_roteiro(self):
        self.segundoAtrativo.ativo = False
        self.segundoAtrativo.save()
        for ids in [[self.primeiroAtrativo.id] * 2, [999999], [self.segundoAtrativo.id]]:
            with self.subTest(ids=ids):
                resposta = self.criarRoteiro({"titulo": "Passeio", "atrativo_ids": ids})
                self.assertEqual(resposta.status_code, 400)
                self.assertFalse(Rota.objects.exists())
                self.assertFalse(RotaAtrativo.objects.exists())

    def test_rejeitar_titulo_vazio_e_ids_invalidos(self):
        self.assertEqual(self.criarRoteiro({"titulo": "   "}).status_code, 400)
        for ids in [[0], [-1], [True], [1.5], ["1"], list(range(1, 102))]:
            with self.subTest(ids=ids):
                self.assertEqual(self.criarRoteiro({"titulo": "Passeio", "atrativo_ids": ids}).status_code, 422)
                self.assertFalse(Rota.objects.exists())

    def test_desfazer_criacao_se_paradas_falharem(self):
        with patch("rotas.router.RotaAtrativo.objects.bulk_create", side_effect=RuntimeError("Falha de teste")):
            with self.assertRaises(RuntimeError):
                self.criarRoteiro({"titulo": "Passeio", "atrativo_ids": [self.primeiroAtrativo.id]})
        self.assertFalse(Rota.objects.exists())
        self.assertFalse(RotaAtrativo.objects.exists())

    def test_preservar_criacao_sem_paradas(self):
        resposta = self.criarRoteiro({"titulo": "Passeio"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json()["itens"], [])
