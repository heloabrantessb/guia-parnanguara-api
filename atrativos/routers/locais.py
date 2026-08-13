from typing import List
from ninja import Router
from atrativos.models import Local, Categoria
from atrativos.schemas import (
    LocalInSchema,
    LocalOutSchema,
    LocalPatchSchema,
    ErrorSchema
)

router = Router(tags=["Locais"])


@router.post("/", response={201: LocalOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def create_local(request, payload: LocalInSchema):
    data = payload.dict(exclude={"categoria_ids"})
    
    # Check if all categories exist before creating the Local
    categorias = []
    if payload.categoria_ids:
        categorias = list(Categoria.objects.filter(id__in=payload.categoria_ids))
        if len(categorias) != len(payload.categoria_ids):
            return 404, {"error": "Uma ou mais categorias não foram encontradas"}

    local = Local.objects.create(**data)
    
    if categorias:
        local.categorias.set(categorias)
        
    return 201, local


@router.get("/", response=List[LocalOutSchema])
def list_locais(request):
    return Local.objects.all()


@router.get("/{local_id}", response={200: LocalOutSchema, 404: ErrorSchema})
def get_local(request, local_id: int):
    try:
        local = Local.objects.get(id=local_id)
        return 200, local
    except Local.DoesNotExist:
        return 404, {"error": "Local não encontrado"}


@router.patch("/{local_id}", response={200: LocalOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def update_local(request, local_id: int, payload: LocalPatchSchema):
    try:
        local = Local.objects.get(id=local_id)
        
        data = payload.dict(exclude_unset=True, exclude={"categoria_ids"})
        for attr, value in data.items():
            setattr(local, attr, value)
            
        if payload.categoria_ids is not None:
            categorias = list(Categoria.objects.filter(id__in=payload.categoria_ids))
            if len(categorias) != len(payload.categoria_ids):
                return 404, {"error": "Uma ou mais categorias não foram encontradas"}
            local.categorias.set(categorias)
            
        local.save()
        return 200, local
    except Local.DoesNotExist:
        return 404, {"error": "Local não encontrado"}


@router.delete("/{local_id}", response={204: None, 404: ErrorSchema})
def delete_local(request, local_id: int):
    try:
        local = Local.objects.get(id=local_id)
        local.delete()
        return 204, None
    except Local.DoesNotExist:
        return 404, {"error": "Local não encontrado"}
