import json
from django.test import TestCase
from atrativos.models import Local, Categoria

class LocalAPITestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(titulo="Praia", tipo="local")
        self.local_data = {
            "nome": "Ilha do Mel",
            "descricao": "Uma bela ilha",
            "endereco": "Baía de Paranaguá",
            "latitude": "-25.556",
            "longitude": "-48.332",
            "ativo": True,
            "valor_entrada": "0.0",
            "horario_abertura": "08:00:00",
            "horario_fechamento": "18:00:00",
            "categoria_ids": [self.categoria.id]
        }

    def test_criar_local(self):
        response = self.client.post(
            "/locais/",
            data=json.dumps(self.local_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nome"], "Ilha do Mel")
        self.assertEqual(len(data["categorias"]), 1)

    def test_listar_locais(self):
        # Primeiro cria
        self.client.post(
            "/locais/",
            data=json.dumps(self.local_data),
            content_type="application/json"
        )
        response = self.client.get("/locais/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_atualizar_local(self):
        # Primeiro cria
        response = self.client.post(
            "/locais/",
            data=json.dumps(self.local_data),
            content_type="application/json"
        )
        local_id = response.json()["id"]

        update_response = self.client.patch(
            f"/locais/{local_id}",
            data=json.dumps({"nome": "Ilha das Peças"}),
            content_type="application/json"
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["nome"], "Ilha das Peças")

    def test_deletar_local(self):
        # Primeiro cria
        response = self.client.post(
            "/locais/",
            data=json.dumps(self.local_data),
            content_type="application/json"
        )
        local_id = response.json()["id"]

        delete_response = self.client.delete(f"/locais/{local_id}")
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(Local.objects.count(), 0)
