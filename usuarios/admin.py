from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from usuarios.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('id', 'nome', 'email', 'funcao', 'is_active', 'criado_em')
    list_filter = ('funcao', 'is_active', 'is_staff')
    search_fields = ('nome', 'email')
    ordering = ('id',)

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('nome', 'funcao', 'foto_perfil')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('nome', 'funcao', 'foto_perfil')}),
    )

