from datetime import datetime, time
from decimal import Decimal
from typing import List, Optional
from ninja import Schema
from pydantic import Field
from atrativos.models import TipoCategoria


class CategoriaInSchema(Schema):
    titulo: str = Field(..., min_length=1, max_length=45)
    tipo: TipoCategoria = TipoCategoria.AMBOS
    ativo: bool = True


class CategoriaPatchSchema(Schema):
    titulo: Optional[str] = Field(None, min_length=1, max_length=45)
    tipo: Optional[TipoCategoria] = None
    ativo: Optional[bool] = None


class CategoriaOutSchema(Schema):
    id: int
    titulo: str
    tipo: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


class AtrativoImagemOutSchema(Schema):
    id: int
    imagem_url: str
    imagem_capa: bool
    criado_em: datetime

    @staticmethod
    def resolve_imagem_url(obj):
        if obj.imagem:
            return obj.imagem.url
        return None


class AtrativoBaseInSchema(Schema):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: str
    endereco: str = Field(..., min_length=1, max_length=255)
    latitude: Decimal
    longitude: Decimal
    ativo: bool = True
    valor_entrada: Optional[Decimal] = None
    categoria_ids: List[int] = Field(default_factory=list)


class AtrativoBasePatchSchema(Schema):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    endereco: Optional[str] = Field(None, min_length=1, max_length=255)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    ativo: Optional[bool] = None
    valor_entrada: Optional[Decimal] = None
    categoria_ids: Optional[List[int]] = None


class AtrativoBaseOutSchema(Schema):
    id: int
    nome: str
    descricao: str
    endereco: str
    latitude: Decimal
    longitude: Decimal
    ativo: bool
    valor_entrada: Optional[Decimal]
    categorias: List[CategoriaOutSchema]
    imagens: List[AtrativoImagemOutSchema]
    criado_em: datetime
    atualizado_em: datetime


class LocalInSchema(AtrativoBaseInSchema):
    horario_abertura: time
    horario_fechamento: time


class LocalPatchSchema(AtrativoBasePatchSchema):
    horario_abertura: Optional[time] = None
    horario_fechamento: Optional[time] = None


class LocalOutSchema(AtrativoBaseOutSchema):
    horario_abertura: time
    horario_fechamento: time


class EventoInSchema(AtrativoBaseInSchema):
    data_inicio: datetime
    data_fim: datetime


class EventoPatchSchema(AtrativoBasePatchSchema):
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None


class EventoOutSchema(AtrativoBaseOutSchema):
    data_inicio: datetime
    data_fim: datetime


class ErrorSchema(Schema):
    error: str
