from typing import List
from ninja import Router, Schema
from usuarios.auth import JWTAuth
from atrativos.models import Categoria
from atrativos.schemas import CategoriaOutSchema, ErrorSchema

router = Router(tags=["Preferências"], auth=JWTAuth())


class DefinirPreferenciasSchema(Schema):
    categoria_ids: List[int]


@router.get("/", response=List[CategoriaOutSchema])
def list_preferencias(request):
    return request.user.preferencias.all()


@router.post("/", response={200: List[CategoriaOutSchema], 400: ErrorSchema})
def set_preferencias(request, payload: DefinirPreferenciasSchema):
    categoria_ids = payload.categoria_ids
    
    if categoria_ids:
        categorias = list(Categoria.objects.filter(id__in=categoria_ids))
        if len(categorias) != len(set(categoria_ids)):
            return 400, {"error": "Uma ou mais categorias não foram encontradas"}
    else:
        categorias = []

    request.user.preferencias.set(categorias)
    return 200, request.user.preferencias.all()


@router.delete("/{categoria_id}", response={204: None, 404: ErrorSchema})
def delete_preferencia(request, categoria_id: int):
    if not request.user.preferencias.filter(id=categoria_id).exists():
        return 404, {"error": "Categoria não encontrada nas preferências do usuário"}
        
    request.user.preferencias.remove(categoria_id)
    return 204, None
