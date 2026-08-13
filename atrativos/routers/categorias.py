from typing import List
from ninja import Router
from atrativos.models import Categoria
from atrativos.schemas import (
    CategoriaInSchema,
    CategoriaOutSchema,
    CategoriaPatchSchema,
    ErrorSchema
)

router = Router(tags=["Categorias"])


@router.post("/", response={201: CategoriaOutSchema, 400: ErrorSchema})
def create_categoria(request, payload: CategoriaInSchema):
    categoria = Categoria.objects.create(**payload.dict())
    return 201, categoria


@router.get("/", response=List[CategoriaOutSchema])
def list_categorias(request):
    return Categoria.objects.all()


@router.get("/{categoria_id}", response={200: CategoriaOutSchema, 404: ErrorSchema})
def get_categoria(request, categoria_id: int):
    try:
        categoria = Categoria.objects.get(id=categoria_id)
        return 200, categoria
    except Categoria.DoesNotExist:
        return 404, {"error": "Categoria não encontrada"}


@router.patch("/{categoria_id}", response={200: CategoriaOutSchema, 404: ErrorSchema})
def update_categoria(request, categoria_id: int, payload: CategoriaPatchSchema):
    try:
        categoria = Categoria.objects.get(id=categoria_id)
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(categoria, attr, value)
        categoria.save()
        return 200, categoria
    except Categoria.DoesNotExist:
        return 404, {"error": "Categoria não encontrada"}


@router.delete("/{categoria_id}", response={204: None, 404: ErrorSchema})
def delete_categoria(request, categoria_id: int):
    try:
        categoria = Categoria.objects.get(id=categoria_id)
        categoria.delete()
        return 204, None
    except Categoria.DoesNotExist:
        return 404, {"error": "Categoria não encontrada"}
