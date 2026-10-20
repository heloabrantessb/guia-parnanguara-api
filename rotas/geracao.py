from dataclasses import dataclass
from datetime import datetime, timedelta
from math import asin, ceil, cos, isfinite, radians, sin, sqrt
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone

from atrativos.models import Atrativo, Categoria
from rotas.models import Rota, RotaAtrativo


fusoParanagua = ZoneInfo("America/Sao_Paulo")
metrosPorMinuto = 75


class ErroGeracaoRota(ValueError):
    pass


@dataclass
class ParadaPlanejada:
    atrativo: Atrativo
    chegadaEm: datetime
    saidaEm: datetime
    deslocamentoMinutos: int
    esperaMinutos: int


def validarCoordenadas(atrativo):
    latitude = float(atrativo.latitude)
    longitude = float(atrativo.longitude)
    return isfinite(latitude) and isfinite(longitude) and -90 <= latitude <= 90 and -180 <= longitude <= 180


def estimarDeslocamento(primeiroAtrativo, segundoAtrativo):
    if primeiroAtrativo is None:
        return 0
    latitudeInicial = radians(float(primeiroAtrativo.latitude))
    latitudeFinal = radians(float(segundoAtrativo.latitude))
    diferencaLongitude = radians(float(segundoAtrativo.longitude) - float(primeiroAtrativo.longitude))
    quadradoSeno = sin((latitudeFinal - latitudeInicial) / 2) ** 2 + cos(latitudeInicial) * cos(latitudeFinal) * sin(diferencaLongitude / 2) ** 2
    distanciaMetros = 2 * 6371000 * asin(sqrt(min(1, max(0, quadradoSeno))))
    return ceil(distanciaMetros / metrosPorMinuto)


def buscarInicioVisita(atrativo, chegadaEm):
    duracaoVisita = timedelta(minutes=atrativo.duracao_visita_minutos)
    evento = getattr(atrativo, "evento", None)
    if evento is not None:
        inicioVisita = max(chegadaEm, evento.data_inicio)
        return inicioVisita if inicioVisita + duracaoVisita <= evento.data_fim else None
    local = getattr(atrativo, "local", None)
    if local is None:
        return chegadaEm

    # A janela do dia anterior cobre locais que permanecem abertos após meia-noite.
    dataChegada = chegadaEm.astimezone(fusoParanagua).date()
    for deslocamentoDias in [-1, 0, 1]:
        dataAbertura = dataChegada + timedelta(days=deslocamentoDias)
        aberturaEm = datetime.combine(dataAbertura, local.horario_abertura, tzinfo=fusoParanagua)
        fechamentoEm = datetime.combine(dataAbertura, local.horario_fechamento, tzinfo=fusoParanagua)
        if fechamentoEm <= aberturaEm:
            fechamentoEm += timedelta(days=1)
        inicioVisita = max(chegadaEm, aberturaEm)
        if inicioVisita + duracaoVisita <= fechamentoEm:
            return inicioVisita
    return None


def selecionarParadas(atrativos, categoriaIds, inicioEm, tempoDisponivelMinutos):
    limiteEm = inicioEm + timedelta(minutes=tempoDisponivelMinutos)
    horarioAtual = inicioEm
    ultimoAtrativo = None
    paradas = []
    candidatos = list(atrativos)
    while candidatos and len(paradas) < 100:
        opcoes = []
        for atrativo in candidatos:
            deslocamentoMinutos = estimarDeslocamento(ultimoAtrativo, atrativo)
            chegadaEm = horarioAtual + timedelta(minutes=deslocamentoMinutos)
            inicioVisita = buscarInicioVisita(atrativo, chegadaEm)
            if inicioVisita is None:
                continue
            esperaMinutos = ceil((inicioVisita - chegadaEm).total_seconds() / 60)
            inicioArredondado = chegadaEm + timedelta(minutes=esperaMinutos)
            if buscarInicioVisita(atrativo, inicioArredondado) != inicioArredondado:
                continue
            saidaEm = chegadaEm + timedelta(minutes=esperaMinutos + atrativo.duracao_visita_minutos)
            if saidaEm > limiteEm:
                continue
            afinidade = sum(categoria.id in categoriaIds for categoria in atrativo.categorias.all())
            parada = ParadaPlanejada(atrativo, chegadaEm, saidaEm, deslocamentoMinutos, esperaMinutos)
            opcoes.append(((-afinidade, (saidaEm - horarioAtual).total_seconds(), atrativo.id), parada))
        if not opcoes:
            break
        _, proximaParada = min(opcoes, key=lambda opcao: opcao[0])
        paradas.append(proximaParada)
        candidatos.remove(proximaParada.atrativo)
        ultimoAtrativo = proximaParada.atrativo
        horarioAtual = proximaParada.saidaEm
    return paradas


def gerarRoteiro(usuario, solicitacao):
    titulo = solicitacao.titulo.strip()
    if not titulo:
        raise ErroGeracaoRota("Informe um nome para o roteiro.")
    categoriaIds = solicitacao.categoria_ids
    if categoriaIds is None:
        categoriaIds = list(usuario.preferencias.filter(ativo=True).values_list("id", flat=True))
    if not categoriaIds:
        raise ErroGeracaoRota("Selecione suas preferências para gerar um roteiro.")
    if len(categoriaIds) != len(set(categoriaIds)):
        raise ErroGeracaoRota("Selecione cada categoria apenas uma vez.")
    if Categoria.objects.filter(id__in=categoriaIds, ativo=True).count() != len(categoriaIds):
        raise ErroGeracaoRota("Uma ou mais categorias não estão disponíveis.")

    inicioEm = solicitacao.inicio_em or timezone.now()
    atrativos = Atrativo.objects.filter(
        ativo=True, categorias__id__in=categoriaIds,
        duracao_visita_minutos__gte=1, duracao_visita_minutos__lte=1440,
    ).select_related("local", "evento").prefetch_related("categorias").distinct().order_by("id")
    candidatos = [atrativo for atrativo in atrativos if validarCoordenadas(atrativo)]
    paradas = selecionarParadas(candidatos, set(categoriaIds), inicioEm, solicitacao.tempo_disponivel_minutos)
    if not paradas:
        raise ErroGeracaoRota("Nenhum atrativo combina com suas preferências e o tempo disponível neste horário.")

    with transaction.atomic():
        rota = Rota.objects.create(
            usuario=usuario, titulo=titulo, inicio_em=inicioEm,
            tempo_disponivel_minutos=solicitacao.tempo_disponivel_minutos,
            duracao_estimada_minutos=ceil((paradas[-1].saidaEm - inicioEm).total_seconds() / 60),
        )
        RotaAtrativo.objects.bulk_create([
            RotaAtrativo(
                rota=rota, atrativo=parada.atrativo, ordem=indice + 1,
                chegada_em=parada.chegadaEm, saida_em=parada.saidaEm,
                deslocamento_minutos=parada.deslocamentoMinutos, espera_minutos=parada.esperaMinutos,
                duracao_visita_minutos=parada.atrativo.duracao_visita_minutos,
            ) for indice, parada in enumerate(paradas)
        ])
    return rota


def limparEstimativas(rota):
    # Alterações manuais invalidam os horários calculados para a sequência anterior.
    rota.itens.update(
        chegada_em=None, saida_em=None, deslocamento_minutos=None,
        espera_minutos=None, duracao_visita_minutos=None,
    )
    rota.tempo_disponivel_minutos = None
    rota.duracao_estimada_minutos = None
    rota.inicio_em = None
    rota.save(update_fields=["tempo_disponivel_minutos", "duracao_estimada_minutos", "inicio_em"])
