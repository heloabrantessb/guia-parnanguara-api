import os
from ninja import Router, File
from ninja.files import UploadedFile
from django.db import transaction
from atrativos.models import Atrativo, AtrativoImagem
from atrativos.schemas import AtrativoImagemOutSchema, ErrorSchema

router = Router(tags=["Atrativos - Imagens"])


@router.post("/{atrativo_id}/imagens", response={201: AtrativoImagemOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def upload_imagem(request, atrativo_id: int, file: UploadedFile = File(...)):
    try:
        atrativo = Atrativo.objects.get(id=atrativo_id)
    except Atrativo.DoesNotExist:
        return 404, {"error": "Atrativo não encontrado"}
        
    # Validar tamanho da imagem (5MB)
    if file.size > 5 * 1024 * 1024:
        return 400, {"error": "O arquivo deve ter no máximo 5MB"}
        
    imagem = AtrativoImagem.objects.create(
        atrativo=atrativo,
        imagem=file,
        imagem_capa=False
    )
    
    # Se for a primeira imagem, defina como capa automaticamente
    if AtrativoImagem.objects.filter(atrativo=atrativo).count() == 1:
        imagem.imagem_capa = True
        imagem.save()
        
    return 201, imagem


@router.patch("/imagens/{imagem_id}/capa", response={200: AtrativoImagemOutSchema, 404: ErrorSchema})
def set_imagem_capa(request, imagem_id: int):
    try:
        imagem = AtrativoImagem.objects.get(id=imagem_id)
    except AtrativoImagem.DoesNotExist:
        return 404, {"error": "Imagem não encontrada"}
        
    with transaction.atomic():
        # Desmarcar capa de todas as outras imagens do atrativo
        AtrativoImagem.objects.filter(atrativo=imagem.atrativo).update(imagem_capa=False)
        # Marcar esta como capa
        imagem.imagem_capa = True
        imagem.save()
        
    return 200, imagem


@router.delete("/imagens/{imagem_id}", response={204: None, 404: ErrorSchema})
def delete_imagem(request, imagem_id: int):
    try:
        imagem = AtrativoImagem.objects.get(id=imagem_id)
        
        # Guardar referência ao atrativo e se era capa
        atrativo = imagem.atrativo
        era_capa = imagem.imagem_capa
        
        # Deleta a imagem física e o registro no banco
        imagem.imagem.delete(save=False)
        imagem.delete()
        
        # Se apagou a capa, promove outra a capa se houver
        if era_capa:
            outra_imagem = AtrativoImagem.objects.filter(atrativo=atrativo).first()
            if outra_imagem:
                outra_imagem.imagem_capa = True
                outra_imagem.save()
                
        return 204, None
    except AtrativoImagem.DoesNotExist:
        return 404, {"error": "Imagem não encontrada"}
