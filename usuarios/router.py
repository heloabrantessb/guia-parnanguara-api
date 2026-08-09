from django.contrib.auth.hashers import make_password
from ninja import Router
from usuarios.auth import JWTAuth, generate_token
from usuarios.models import FuncaoUsuario, Usuario
from usuarios.schemas import (
    ErrorOutSchema,
    LoginResponseOutSchema,
    LoginSchema,
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
    if not user or not user.check_password(data.senha):
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
