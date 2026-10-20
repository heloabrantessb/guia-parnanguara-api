from typing import List
from ninja import Router
from django.db import transaction
from usuarios.auth import JWTAuth
from atrativos.models import Atrativo
from rotas.models import Rota, RotaAtrativo
from rotas.geracao import ErroGeracaoRota, gerarRoteiro, limparEstimativas
from rotas.schemas import (
    RotaInSchema,
    RotaOutSchema,
    RotaPatchSchema,
    AdicionarAtrativoSchema,
    ErrorSchema,
    GerarRotaSchema,
)

router = Router(tags=["Roteiros"], auth=JWTAuth())


@router.post("/gerar", response={201: RotaOutSchema, 400: ErrorSchema})
def gerar_rota(request, payload: GerarRotaSchema):
    try:
        rota = gerarRoteiro(request.user, payload)
    except ErroGeracaoRota as erro:
        return 400, {"error": str(erro)}
    return 201, rota


@router.post("/", response={201: RotaOutSchema, 400: ErrorSchema})
def create_rota(request, payload: RotaInSchema):
    titulo = payload.titulo.strip()
    if not titulo:
        return 400, {"error": "Informe um nome para o roteiro."}
    if len(payload.atrativo_ids) != len(set(payload.atrativo_ids)):
        return 400, {"error": "Selecione cada atrativo apenas uma vez."}

    with transaction.atomic():
        atrativos = list(Atrativo.objects.filter(id__in=payload.atrativo_ids, ativo=True))
        if len(atrativos) != len(payload.atrativo_ids):
            return 400, {"error": "Um ou mais atrativos não estão disponíveis."}
        rota = Rota.objects.create(usuario=request.user, titulo=titulo)
        RotaAtrativo.objects.bulk_create([
            RotaAtrativo(rota=rota, atrativo_id=atrativoId, ordem=indice + 1)
            for indice, atrativoId in enumerate(payload.atrativo_ids)
        ])
    return 201, rota


@router.get("/", response=List[RotaOutSchema])
def list_rotas(request):
    return Rota.objects.filter(usuario=request.user)


@router.get("/{rota_id}", response={200: RotaOutSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_rota(request, rota_id: int):
    try:
        rota = Rota.objects.get(id=rota_id)
        if rota.usuario != request.user:
            return 403, {"error": "Acesso negado"}
        return 200, rota
    except Rota.DoesNotExist:
        return 404, {"error": "Rota não encontrada"}


@router.patch("/{rota_id}", response={200: RotaOutSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_rota(request, rota_id: int, payload: RotaPatchSchema):
    try:
        rota = Rota.objects.get(id=rota_id)
        if rota.usuario != request.user:
            return 403, {"error": "Acesso negado"}
            
        if payload.titulo:
            rota.titulo = payload.titulo
            rota.save()
            
        return 200, rota
    except Rota.DoesNotExist:
        return 404, {"error": "Rota não encontrada"}


@router.delete("/{rota_id}", response={204: None, 403: ErrorSchema, 404: ErrorSchema})
def delete_rota(request, rota_id: int):
    try:
        rota = Rota.objects.get(id=rota_id)
        if rota.usuario != request.user:
            return 403, {"error": "Acesso negado"}
            
        rota.delete()
        return 204, None
    except Rota.DoesNotExist:
        return 404, {"error": "Rota não encontrada"}


@router.post("/{rota_id}/atrativos", response={201: RotaOutSchema, 400: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def add_atrativo_to_rota(request, rota_id: int, payload: AdicionarAtrativoSchema):
    try:
        rota = Rota.objects.get(id=rota_id)
        if rota.usuario != request.user:
            return 403, {"error": "Acesso negado"}
    except Rota.DoesNotExist:
        return 404, {"error": "Rota não encontrada"}

    try:
        atrativo = Atrativo.objects.get(id=payload.atrativo_id)
    except Atrativo.DoesNotExist:
        return 404, {"error": "Atrativo não encontrado"}

    if RotaAtrativo.objects.filter(rota=rota, atrativo=atrativo).exists():
        return 400, {"error": "Atrativo já cadastrado neste roteiro"}

    with transaction.atomic():
        RotaAtrativo.objects.create(
            rota=rota,
            atrativo=atrativo,
            ordem=payload.ordem
        )
        if rota.inicio_em is not None:
            limparEstimativas(rota)
    return 201, rota


@router.delete("/{rota_id}/atrativos/{atrativo_id}", response={200: RotaOutSchema, 403: ErrorSchema, 404: ErrorSchema})
def remove_atrativo_from_rota(request, rota_id: int, atrativo_id: int):
    try:
        rota = Rota.objects.get(id=rota_id)
        if rota.usuario != request.user:
            return 403, {"error": "Acesso negado"}
    except Rota.DoesNotExist:
        return 404, {"error": "Rota não encontrada"}

    try:
        item = RotaAtrativo.objects.get(rota=rota, atrativo_id=atrativo_id)
    except RotaAtrativo.DoesNotExist:
        return 404, {"error": "Atrativo não cadastrado neste roteiro"}

    with transaction.atomic():
        item.delete()
        
        # Reordenar itens restantes para manter sequência contínua 1..N
        itens = RotaAtrativo.objects.filter(rota=rota).order_by('ordem', 'id')
        for index, elem in enumerate(itens, start=1):
            if elem.ordem != index:
                elem.ordem = index
                elem.save()
        if rota.inicio_em is not None:
            limparEstimativas(rota)

    return 200, rota
