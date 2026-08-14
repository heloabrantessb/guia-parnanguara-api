from django.contrib import admin
from rotas.models import Rota, RotaAtrativo


class RotaAtrativoInline(admin.TabularInline):
    model = RotaAtrativo
    extra = 1
    ordering = ('ordem',)


@admin.register(Rota)
class RotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'usuario', 'criado_em')
    search_fields = ('titulo', 'usuario__email', 'usuario__nome')
    inlines = [RotaAtrativoInline]
