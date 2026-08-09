from datetime import datetime
from typing import Optional
from ninja import Schema
from pydantic import EmailStr, Field


class RegistroSchema(Schema):
    nome: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    senha: str = Field(..., min_length=6)


class LoginSchema(Schema):
    email: EmailStr
    senha: str


class UsuarioOutSchema(Schema):
    id: int
    nome: str
    email: str
    funcao: str
    foto_perfil: Optional[str] = None
    criado_em: datetime


class LoginResponseOutSchema(Schema):
    usuario: UsuarioOutSchema
    token: str


class ErrorOutSchema(Schema):
    error: str


class AtualizarPerfilSchema(Schema):
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    foto_perfil: Optional[str] = None
    email: Optional[EmailStr] = None
    senha_atual: Optional[str] = None
    nova_senha: Optional[str] = Field(None, min_length=6)


class MessageOutSchema(Schema):
    message: str
