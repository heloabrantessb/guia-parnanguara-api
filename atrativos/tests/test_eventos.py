import json
from django.test import TestCase
from atrativos.models import Evento, Categoria

class EventoAPITestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(titulo="Festa", tipo="evento")
        self.evento_data = {
            "nome": "Festa do Rocio",
            "descricao": "Maior festa do sul do Brasil",
            "endereco": "Praça da Fé",
            "latitude": "-25.556",
            "longitude": "-48.332",
            "ativo": True,
            "valor_entrada": "0.0",
            "data_inicio": "2027-11-01T08:00:00Z",
            "data_fim": "2027-11-15T23:59:59Z",
            "categoria_ids": [self.categoria.id]
        }

    def test_criar_evento(self):
        response = self.client.post(
            "/eventos/",
            data=json.dumps(self.evento_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nome"], "Festa do Rocio")
        self.assertEqual(len(data["categorias"]), 1)

    def test_listar_eventos(self):
        self.client.post(
            "/eventos/",
            data=json.dumps(self.evento_data),
            content_type="application/json"
        )
        response = self.client.get("/eventos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_atualizar_evento(self):
        response = self.client.post(
            "/eventos/",
            data=json.dumps(self.evento_data),
            content_type="application/json"
        )
        evento_id = response.json()["id"]

        update_response = self.client.patch(
            f"/eventos/{evento_id}",
            data=json.dumps({"nome": "Festa de NS do Rocio"}),
            content_type="application/json"
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["nome"], "Festa de NS do Rocio")

    def test_deletar_evento(self):
        response = self.client.post(
            "/eventos/",
            data=json.dumps(self.evento_data),
            content_type="application/json"
        )
        evento_id = response.json()["id"]

        delete_response = self.client.delete(f"/eventos/{evento_id}")
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(Evento.objects.count(), 0)
