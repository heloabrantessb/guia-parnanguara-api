from copy import deepcopy
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from atrativos.management.commands.popular_atrativos import carregarCatalogo
from atrativos.models import Atrativo, AtrativoImagem, Categoria, Evento, Local


class PopularAtrativosTestCase(TestCase):
    def popularCatalogo(self):
        saida = StringIO()
        call_command("popular_atrativos", stdout=saida)
        return saida.getvalue()

    def test_carregar_catalogo_real_com_coordenadas_e_categorias(self):
        saida = self.popularCatalogo()
        self.assertEqual(Local.objects.count(), 8)
        self.assertEqual(Atrativo.objects.count(), 8)
        self.assertEqual(Evento.objects.count(), 0)
        self.assertEqual(AtrativoImagem.objects.count(), 0)
        self.assertIn("8 locais criados", saida)
        for local in Local.objects.all():
            self.assertTrue(local.categorias.exists())
            self.assertTrue(local.ativo)
            self.assertGreater(local.duracao_visita_minutos, 0)
            self.assertTrue(-26 < local.latitude < -25)
            self.assertTrue(-49 < local.longitude < -48)

    def test_repetir_comando_sem_duplicar_registros(self):
        self.popularCatalogo()
        idsLocais = list(Local.objects.values_list("id", flat=True))
        idsCategorias = list(Categoria.objects.values_list("id", flat=True))
        saida = self.popularCatalogo()
        self.assertEqual(list(Local.objects.values_list("id", flat=True)), idsLocais)
        self.assertEqual(list(Categoria.objects.values_list("id", flat=True)), idsCategorias)
        self.assertIn("0 locais criados; 8 registros preservados", saida)

    def test_preservar_edicoes_imagens_categorias_e_atividade(self):
        museu = Local.objects.create(
            nome="Museu de Arqueologia e Etnologia da UFPR", descricao="Descrição cadastrada manualmente",
            endereco="Endereço cadastrado", latitude="-25.52156168", longitude="-48.50709010",
            horario_abertura="08:00", horario_fechamento="20:00", duracao_visita_minutos=60, ativo=False,
        )
        categoria = Categoria.objects.create(titulo="Categoria própria")
        museu.categorias.set([categoria])
        imagem = AtrativoImagem.objects.create(atrativo=museu, imagem="atrativos/foto-existente.jpeg", imagem_capa=True)
        self.popularCatalogo()
        museu.refresh_from_db()
        self.assertEqual(museu.descricao, "Descrição cadastrada manualmente")
        self.assertEqual(museu.endereco, "Endereço cadastrado")
        self.assertEqual(str(museu.horario_abertura), "08:00:00")
        self.assertEqual(museu.duracao_visita_minutos, 60)
        self.assertFalse(museu.ativo)
        self.assertEqual(list(museu.categorias.all()), [categoria])
        self.assertTrue(AtrativoImagem.objects.filter(id=imagem.id, imagem="atrativos/foto-existente.jpeg").exists())
        self.assertEqual(Local.objects.count(), 8)

    def test_reconhecer_nomes_sem_acentos_ou_com_caixa_diferente(self):
        categoria = Categoria.objects.create(titulo="historico", ativo=False)
        existente = Atrativo.objects.create(
            nome="  IGREJA DE SAO BENEDITO ", descricao="Original", endereco="Original",
            latitude="-25.52", longitude="-48.51",
        )
        self.popularCatalogo()
        self.assertEqual(Atrativo.objects.count(), 8)
        self.assertEqual(Local.objects.count(), 7)
        self.assertTrue(Atrativo.objects.filter(id=existente.id, descricao="Original").exists())
        self.assertFalse(Categoria.objects.filter(titulo="Histórico").exists())
        categoria.refresh_from_db()
        self.assertFalse(categoria.ativo)

    def test_desfazer_carga_inteira_se_persistencia_falhar(self):
        with patch("atrativos.management.commands.popular_atrativos.Local.save", side_effect=RuntimeError("Falha de teste")):
            with self.assertRaises(RuntimeError):
                self.popularCatalogo()
        self.assertFalse(Atrativo.objects.exists())
        self.assertFalse(Categoria.objects.exists())

    def test_rejeitar_catalogo_invalido_sem_criar_categorias(self):
        with patch("atrativos.management.commands.popular_atrativos.caminhoCatalogo") as caminho:
            caminho.read_text.return_value = '{"atrativos": []}'
            with self.assertRaises(CommandError):
                self.popularCatalogo()
        self.assertFalse(Atrativo.objects.exists())
        self.assertFalse(Categoria.objects.exists())

    def test_rejeitar_coordenadas_fora_do_intervalo(self):
        import json
        from atrativos.management.commands.popular_atrativos import caminhoCatalogo
        catalogo = json.loads(caminhoCatalogo.read_text())
        catalogoInvalido = deepcopy(catalogo)
        catalogoInvalido["atrativos"][0]["latitude"] = "91.0"
        with patch("atrativos.management.commands.popular_atrativos.caminhoCatalogo") as caminho:
            caminho.read_text.return_value = json.dumps(catalogoInvalido)
            with self.assertRaises(CommandError):
                carregarCatalogo()
        self.assertFalse(Atrativo.objects.exists())
