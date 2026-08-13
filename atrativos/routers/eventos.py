from typing import List
from ninja import Router
from atrativos.models import Evento, Categoria
from atrativos.schemas import (
    EventoInSchema,
    EventoOutSchema,
    EventoPatchSchema,
    ErrorSchema
)

router = Router(tags=["Eventos"])


@router.post("/", response={201: EventoOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def create_evento(request, payload: EventoInSchema):
    data = payload.dict(exclude={"categoria_ids"})
    
    # Check if all categories exist before creating the Evento
    categorias = []
    if payload.categoria_ids:
        categorias = list(Categoria.objects.filter(id__in=payload.categoria_ids))
        if len(categorias) != len(payload.categoria_ids):
            return 404, {"error": "Uma ou mais categorias não foram encontradas"}

    evento = Evento.objects.create(**data)
    
    if categorias:
        evento.categorias.set(categorias)
        
    return 201, evento


@router.get("/", response=List[EventoOutSchema])
def list_eventos(request):
    return Evento.objects.all()


@router.get("/{evento_id}", response={200: EventoOutSchema, 404: ErrorSchema})
def get_evento(request, evento_id: int):
    try:
        evento = Evento.objects.get(id=evento_id)
        return 200, evento
    except Evento.DoesNotExist:
        return 404, {"error": "Evento não encontrado"}


@router.patch("/{evento_id}", response={200: EventoOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def update_evento(request, evento_id: int, payload: EventoPatchSchema):
    try:
        evento = Evento.objects.get(id=evento_id)
        
        data = payload.dict(exclude_unset=True, exclude={"categoria_ids"})
        for attr, value in data.items():
            setattr(evento, attr, value)
            
        if payload.categoria_ids is not None:
            categorias = list(Categoria.objects.filter(id__in=payload.categoria_ids))
            if len(categorias) != len(payload.categoria_ids):
                return 404, {"error": "Uma ou mais categorias não foram encontradas"}
            evento.categorias.set(categorias)
            
        evento.save()
        return 200, evento
    except Evento.DoesNotExist:
        return 404, {"error": "Evento não encontrado"}


@router.delete("/{evento_id}", response={204: None, 404: ErrorSchema})
def delete_evento(request, evento_id: int):
    try:
        evento = Evento.objects.get(id=evento_id)
        evento.delete()
        return 204, None
    except Evento.DoesNotExist:
        return 404, {"error": "Evento não encontrado"}
