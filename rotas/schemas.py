from datetime import datetime
from typing import Annotated, List, Optional
from ninja import Schema
from pydantic import Field
from atrativos.schemas import AtrativoBaseOutSchema


class RotaInSchema(Schema):
    titulo: str = Field(..., min_length=1, max_length=255)
    atrativo_ids: List[Annotated[int, Field(strict=True, gt=0)]] = Field(default_factory=list, max_length=100)


class RotaPatchSchema(Schema):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)


class AdicionarAtrativoSchema(Schema):
    atrativo_id: int
    ordem: int = Field(..., ge=1)


class RotaItemOutSchema(Schema):
    id: int
    ordem: int
    atrativo: AtrativoBaseOutSchema


class RotaOutSchema(Schema):
    id: int
    titulo: str
    criado_em: datetime
    itens: List[RotaItemOutSchema]


class ErrorSchema(Schema):
    error: str
