from django.contrib import admin
from atrativos.models import Categoria, Atrativo, Local, Evento, AtrativoImagem

class AtrativoImagemInline(admin.TabularInline):
    model = AtrativoImagem
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'tipo', 'ativo', 'criado_em')
    list_filter = ('tipo', 'ativo')
    search_fields = ('titulo',)

@admin.register(Atrativo)
class AtrativoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')
    inlines = [AtrativoImagemInline]

@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'horario_abertura', 'horario_fechamento', 'ativo')
    search_fields = ('nome', 'descricao', 'endereco')
    filter_horizontal = ('categorias',)
    inlines = [AtrativoImagemInline]

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'data_inicio', 'data_fim', 'ativo')
    search_fields = ('nome', 'descricao', 'endereco')
    filter_horizontal = ('categorias',)
    inlines = [AtrativoImagemInline]

