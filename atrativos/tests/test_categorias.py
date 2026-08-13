import json
from django.test import TestCase
from atrativos.models import Categoria

class CategoriaAPITestCase(TestCase):
    def setUp(self):
        self.categoria_data = {
            "titulo": "Museus",
            "tipo": "ambos",
            "ativo": True
        }

    def test_criar_categoria(self):
        response = self.client.post(
            "/v1/categorias/",
            data=json.dumps(self.categoria_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["titulo"], "Museus")

    def test_listar_categorias(self):
        Categoria.objects.create(**self.categoria_data)
        response = self.client.get("/v1/categorias/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_atualizar_categoria(self):
        categoria = Categoria.objects.create(**self.categoria_data)
        response = self.client.patch(
            f"/v1/categorias/{categoria.id}",
            data=json.dumps({"titulo": "Museus Históricos"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["titulo"], "Museus Históricos")

    def test_deletar_categoria(self):
        categoria = Categoria.objects.create(**self.categoria_data)
        response = self.client.delete(f"/v1/categorias/{categoria.id}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Categoria.objects.count(), 0)
