from django.contrib.auth.models import AbstractUser
from django.db import models


class FuncaoUsuario(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    USUARIO = 'usuario', 'Usuario'


class Usuario(AbstractUser):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    funcao = models.CharField(
        max_length=20,
        choices=FuncaoUsuario.choices,
        default=FuncaoUsuario.USUARIO,
    )
    foto_perfil = models.CharField(max_length=500, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    desativado_em = models.DateTimeField(null=True, blank=True)

    # coloca o email como identificador único do usuário
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'username']

    # método personalizado para salvar o campo username como o mesmo do email 
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.email})"
