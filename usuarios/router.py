from django.contrib.auth.hashers import make_password
from django.utils import timezone
from ninja import Router
from usuarios.auth import JWTAuth, generate_token
from usuarios.models import FuncaoUsuario, Usuario
from usuarios.schemas import (
    AtualizarPerfilSchema,
    ErrorOutSchema,
    LoginResponseOutSchema,
    LoginSchema,
    MessageOutSchema,
    RegistroSchema,
    UsuarioOutSchema,
)

router = Router(tags=["Usuários"])


@router.post(
    "/registro",
    response={201: UsuarioOutSchema, 409: ErrorOutSchema},
    auth=None,
)
def registro(request, data: RegistroSchema):
    if Usuario.objects.filter(email=data.email).exists():
        return 409, {"error": "Email já cadastrado"}

    user = Usuario.objects.create(
        nome=data.nome,
        email=data.email,
        username=data.email,
        password=make_password(data.senha),
        funcao=FuncaoUsuario.USUARIO,
    )
    return 201, user


@router.post(
    "/login",
    response={200: LoginResponseOutSchema, 401: ErrorOutSchema},
    auth=None,
)
def login(request, data: LoginSchema):
    user = Usuario.objects.filter(email=data.email).first()
    if not user or not user.is_active or not user.check_password(data.senha):
        return 401, {"error": "Email ou senha inválidos"}

    token = generate_token(user)
    return 200, {"usuario": user, "token": token}


@router.get(
    "/perfil",
    response={200: UsuarioOutSchema, 401: ErrorOutSchema},
    auth=JWTAuth(),
)
def perfil(request):
    return 200, request.user


@router.put(
    "/perfil",
    response={200: UsuarioOutSchema, 400: ErrorOutSchema, 409: ErrorOutSchema, 401: ErrorOutSchema},
    auth=JWTAuth(),
)
def atualizar_perfil(request, data: AtualizarPerfilSchema):
    user = request.user

    if data.email and data.email != user.email:
        if Usuario.objects.filter(email=data.email).exclude(id=user.id).exists():
            return 409, {"error": "Email já cadastrado"}
        user.email = data.email
        user.username = data.email

    if data.nome is not None:
        user.nome = data.nome

    if data.foto_perfil is not None:
        user.foto_perfil = data.foto_perfil

    if data.nova_senha:
        if not data.senha_atual or not user.check_password(data.senha_atual):
            return 400, {"error": "Senha atual incorreta"}
        user.set_password(data.nova_senha)

    user.save()
    return 200, user


@router.delete(
    "/perfil",
    response={200: MessageOutSchema, 401: ErrorOutSchema},
    auth=JWTAuth(),
)
def deletar_perfil(request):
    user = request.user
    user.is_active = False
    user.desativado_em = timezone.now()
    user.save()
    return 200, {"message": "Conta desativada com sucesso"}

