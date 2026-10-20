import json
from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import TestCase

from atrativos.models import Categoria, Evento, Local
from rotas.models import Rota, RotaAtrativo
from usuarios.auth import generate_token
from usuarios.models import Usuario


class GeracaoRoteirosAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            username="passeio@example.com", email="passeio@example.com", nome="Maria", password="senha-de-teste",
        )
        cls.outraPessoa = Usuario.objects.create_user(
            username="outro@example.com", email="outro@example.com", nome="João", password="senha-de-teste",
        )
        cls.cultura = Categoria.objects.create(titulo="Cultura")
        cls.natureza = Categoria.objects.create(titulo="Natureza")
        cls.usuario.preferencias.set([cls.cultura])
        cls.inicioEm = datetime(2026, 10, 20, 9, tzinfo=ZoneInfo("America/Sao_Paulo"))

    def setUp(self):
        self.cabecalhos = {"HTTP_AUTHORIZATION": f"Bearer {generate_token(self.usuario)}"}

    def criarLocal(self, **campos):
        local = Local.objects.create(**{
            "nome": "Museu", "descricao": "Visita cultural", "endereco": "Centro",
            "latitude": "-25.52", "longitude": "-48.50",
            "horario_abertura": "08:00", "horario_fechamento": "18:00", **campos,
        })
        local.categorias.set([self.cultura])
        return local

    def gerarRoteiro(self, corpo=None, cabecalhos=None):
        solicitacao = {"titulo": "Passeio", "tempo_disponivel_minutos": 60, "inicio_em": self.inicioEm.isoformat()}
        solicitacao.update(corpo or {})
        return self.client.post(
            "/v1/rotas/gerar", data=json.dumps(solicitacao), content_type="application/json",
            **(self.cabecalhos if cabecalhos is None else cabecalhos),
        )

    def test_exigir_token_valido_de_usuario_ativo(self):
        self.criarLocal()
        for cabecalhos in [{}, {"HTTP_AUTHORIZATION": "Bearer invalido"}]:
            self.assertEqual(self.gerarRoteiro(cabecalhos=cabecalhos).status_code, 401)
        self.usuario.is_active = False
        self.usuario.save()
        self.assertEqual(self.gerarRoteiro().status_code, 401)
        self.assertFalse(Rota.objects.exists())

    def test_usar_preferencias_salvas_e_isolar_proprietario(self):
        primeiroLocal = self.criarLocal()
        segundoLocal = self.criarLocal(nome="Igreja")
        resposta = self.gerarRoteiro()
        self.assertEqual(resposta.status_code, 201)
        roteiro = resposta.json()
        self.assertEqual(roteiro["duracao_estimada_minutos"], 60)
        self.assertEqual(roteiro["tempo_disponivel_minutos"], 60)
        self.assertEqual([item["atrativo"]["id"] for item in roteiro["itens"]], [primeiroLocal.id, segundoLocal.id])
        self.assertEqual([item["ordem"] for item in roteiro["itens"]], [1, 2])
        self.assertEqual(Rota.objects.get(id=roteiro["id"]).usuario_id, self.usuario.id)
        cabecalhosOutraPessoa = {"HTTP_AUTHORIZATION": f"Bearer {generate_token(self.outraPessoa)}"}
        self.assertEqual(self.client.get(f'/v1/rotas/{roteiro["id"]}', **cabecalhosOutraPessoa).status_code, 403)
        self.assertEqual(self.client.get("/v1/rotas/", **cabecalhosOutraPessoa).json(), [])

    def test_respeitar_categorias_explicitas_sem_sobrescrever_preferencias(self):
        self.criarLocal()
        praca = self.criarLocal(nome="Praça")
        praca.categorias.set([self.natureza])
        resposta = self.gerarRoteiro({"categoria_ids": [self.natureza.id]})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual([item["atrativo"]["id"] for item in resposta.json()["itens"]], [praca.id])
        self.assertEqual(list(self.usuario.preferencias.all()), [self.cultura])

    def test_rejeitar_preferencias_ausentes_duplicadas_inativas_e_inexistentes(self):
        self.usuario.preferencias.clear()
        self.assertEqual(self.gerarRoteiro().status_code, 400)
        self.natureza.ativo = False
        self.natureza.save()
        for ids in [[self.cultura.id, self.cultura.id], [self.natureza.id], [999999]]:
            self.assertEqual(self.gerarRoteiro({"categoria_ids": ids}).status_code, 400)
        self.assertFalse(Rota.objects.exists())

    def test_rejeitar_tempo_invalido_e_inicio_sem_fuso(self):
        for tempo in [0, -1, 1441, 1.5, True, "60", None]:
            with self.subTest(tempo=tempo):
                self.assertEqual(self.gerarRoteiro({"tempo_disponivel_minutos": tempo}).status_code, 422)
        self.assertEqual(self.gerarRoteiro({"inicio_em": "2026-10-20T09:00:00"}).status_code, 422)
        self.assertEqual(self.gerarRoteiro({"categoria_ids": []}).status_code, 422)
        self.assertEqual(self.gerarRoteiro({"titulo": "   "}).status_code, 400)
        self.assertFalse(Rota.objects.exists())

    def test_nao_salvar_roteiro_quando_tempo_insuficiente(self):
        self.criarLocal()
        self.assertEqual(self.gerarRoteiro({"tempo_disponivel_minutos": 29}).status_code, 400)
        self.assertFalse(Rota.objects.exists())
        self.assertFalse(RotaAtrativo.objects.exists())
        resposta = self.gerarRoteiro({"tempo_disponivel_minutos": 30})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json()["duracao_estimada_minutos"], 30)

    def test_filtrar_atrativos_inativos_e_categorias_diferentes(self):
        self.criarLocal(ativo=False)
        outroLocal = self.criarLocal()
        outroLocal.categorias.set([self.natureza])
        self.assertEqual(self.gerarRoteiro().status_code, 400)
        self.assertFalse(Rota.objects.exists())

    def test_contabilizar_caminhada_e_duracao_personalizada(self):
        self.criarLocal(duracao_visita_minutos=10)
        self.criarLocal(nome="Outro museu", latitude="-25.53", duracao_visita_minutos=10)
        curto = self.gerarRoteiro({"tempo_disponivel_minutos": 20}).json()
        self.assertEqual(len(curto["itens"]), 1)
        longo = self.gerarRoteiro({"tempo_disponivel_minutos": 40}).json()
        self.assertEqual(len(longo["itens"]), 2)
        self.assertGreater(longo["itens"][1]["deslocamento_minutos"], 0)
        somaMinutos = sum(item["duracao_visita_minutos"] + item["deslocamento_minutos"] + item["espera_minutos"] for item in longo["itens"])
        self.assertEqual(longo["duracao_estimada_minutos"], somaMinutos)
        self.assertLessEqual(somaMinutos, 40)
        self.assertEqual(datetime.fromisoformat(longo["itens"][-1]["saida_em"]) - self.inicioEm, timedelta(minutes=somaMinutos))

    def test_contabilizar_espera_ate_abertura(self):
        self.criarLocal(horario_abertura="10:00")
        self.assertEqual(self.gerarRoteiro({"tempo_disponivel_minutos": 89}).status_code, 400)
        resposta = self.gerarRoteiro({"tempo_disponivel_minutos": 90}).json()
        self.assertEqual(resposta["duracao_estimada_minutos"], 90)
        self.assertEqual(resposta["itens"][0]["espera_minutos"], 60)

    def test_excluir_local_sem_tempo_antes_do_fechamento(self):
        self.criarLocal(horario_fechamento="09:15")
        self.assertEqual(self.gerarRoteiro().status_code, 400)

    def test_permitir_horario_noturno_depois_da_meia_noite(self):
        self.criarLocal(horario_abertura="22:00", horario_fechamento="02:00")
        resposta = self.gerarRoteiro({"inicio_em": "2026-10-21T00:30:00-03:00"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json()["duracao_estimada_minutos"], 30)

    def test_evento_respeita_inicio_fim_e_espera(self):
        evento = Evento.objects.create(
            nome="Exposição", descricao="Arte", endereco="Centro", latitude="-25.52", longitude="-48.50",
            data_inicio=self.inicioEm + timedelta(minutes=30), data_fim=self.inicioEm + timedelta(minutes=60),
        )
        evento.categorias.set([self.cultura])
        self.assertEqual(self.gerarRoteiro({"tempo_disponivel_minutos": 59}).status_code, 400)
        resposta = self.gerarRoteiro().json()
        self.assertEqual(resposta["duracao_estimada_minutos"], 60)
        self.assertEqual(resposta["itens"][0]["espera_minutos"], 30)
        evento.data_fim = self.inicioEm - timedelta(minutes=1)
        evento.save()
        self.assertEqual(self.gerarRoteiro().status_code, 400)

    def test_arredondar_espera_sem_ultrapassar_fim_do_evento(self):
        evento = Evento.objects.create(
            nome="Exposição", descricao="Arte", endereco="Centro", latitude="-25.52", longitude="-48.50",
            data_inicio=self.inicioEm + timedelta(seconds=30), data_fim=self.inicioEm + timedelta(minutes=30, seconds=30),
        )
        evento.categorias.set([self.cultura])
        self.assertEqual(self.gerarRoteiro().status_code, 400)

    def test_rollback_se_persistencia_de_paradas_falhar(self):
        self.criarLocal()
        with patch("rotas.geracao.RotaAtrativo.objects.bulk_create", side_effect=RuntimeError("Falha de teste")):
            with self.assertRaises(RuntimeError):
                self.gerarRoteiro()
        self.assertFalse(Rota.objects.exists())
        self.assertFalse(RotaAtrativo.objects.exists())

    def test_edicao_manual_limpa_estimativas_antigas(self):
        self.criarLocal()
        roteiro = self.gerarRoteiro().json()
        outroLocal = self.criarLocal(nome="Outra parada")
        resposta = self.client.post(
            f'/v1/rotas/{roteiro["id"]}/atrativos',
            data=json.dumps({"atrativo_id": outroLocal.id, "ordem": 2}),
            content_type="application/json", **self.cabecalhos,
        )
        self.assertEqual(resposta.status_code, 201)
        self.assertIsNone(resposta.json()["duracao_estimada_minutos"])
        self.assertTrue(all(item["chegada_em"] is None for item in resposta.json()["itens"]))

    def test_duracao_de_visita_valida_no_catalogo(self):
        local = self.criarLocal()
        for duracao in [0, -1, 1441, None]:
            resposta = self.client.patch(f"/v1/locais/{local.id}", data=json.dumps({"duracao_visita_minutos": duracao}), content_type="application/json")
            self.assertEqual(resposta.status_code, 422)
        local.refresh_from_db()
        self.assertEqual(local.duracao_visita_minutos, 30)
