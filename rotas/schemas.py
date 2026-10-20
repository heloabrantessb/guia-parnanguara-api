from datetime import datetime
from typing import Annotated, List, Optional
from ninja import Schema
from pydantic import AwareDatetime, Field
from atrativos.schemas import AtrativoBaseOutSchema


class RotaInSchema(Schema):
    titulo: str = Field(..., min_length=1, max_length=255)
    atrativo_ids: List[Annotated[int, Field(strict=True, gt=0)]] = Field(default_factory=list, max_length=100)


class RotaPatchSchema(Schema):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)


class GerarRotaSchema(Schema):
    titulo: str = Field(..., min_length=1, max_length=255)
    tempo_disponivel_minutos: int = Field(..., strict=True, ge=1, le=1440)
    categoria_ids: Optional[List[Annotated[int, Field(strict=True, gt=0)]]] = Field(None, min_length=1, max_length=100)
    inicio_em: Optional[AwareDatetime] = None


class AdicionarAtrativoSchema(Schema):
    atrativo_id: int
    ordem: int = Field(..., ge=1)


class RotaItemOutSchema(Schema):
    id: int
    ordem: int
    atrativo: AtrativoBaseOutSchema
    chegada_em: Optional[datetime] = None
    saida_em: Optional[datetime] = None
    deslocamento_minutos: Optional[int] = None
    espera_minutos: Optional[int] = None
    duracao_visita_minutos: Optional[int] = None


class RotaOutSchema(Schema):
    id: int
    titulo: str
    criado_em: datetime
    itens: List[RotaItemOutSchema]
    tempo_disponivel_minutos: Optional[int] = None
    duracao_estimada_minutos: Optional[int] = None
    inicio_em: Optional[datetime] = None


class ErrorSchema(Schema):
    error: str
