import json
import unicodedata
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from atrativos.models import Atrativo, Categoria, Local, TipoCategoria


caminhoCatalogo = Path(__file__).resolve().parents[2] / "catalogo" / "paranagua.json"


def normalizarNome(nome):
    nomeSemAcentos = "".join(
        caractere for caractere in unicodedata.normalize("NFKD", nome)
        if not unicodedata.combining(caractere)
    )
    return " ".join(nomeSemAcentos.casefold().split())


def carregarCatalogo():
    try:
        catalogo = json.loads(caminhoCatalogo.read_text(encoding="utf-8"))
        registros = catalogo["atrativos"]
        if not isinstance(registros, list) or not registros:
            raise ValueError("O catálogo precisa conter atrativos.")
        nomesCatalogo = set()
        locaisValidados = []
        for registro in registros:
            camposLocal = {chave: valor for chave, valor in registro.items() if chave not in {"categorias", "fontes"}}
            local = Local(**camposLocal)
            local.full_clean()
            if not -90 <= local.latitude <= 90 or not -180 <= local.longitude <= 180:
                raise ValueError("Coordenadas fora dos limites geográficos.")
            if local.valor_entrada is not None and local.valor_entrada < 0:
                raise ValueError("O valor de entrada não pode ser negativo.")
            categorias = registro["categorias"]
            if not categorias or any(not isinstance(titulo, str) or not titulo.strip() or len(titulo) > 45 for titulo in categorias):
                raise ValueError("Categorias ausentes ou inválidas.")
            if not registro["fontes"] or any(not fonte["url"].startswith("https://") for fonte in registro["fontes"]):
                raise ValueError("Informe fontes públicas HTTPS para cada atrativo.")
            nomeNormalizado = normalizarNome(local.nome)
            if nomeNormalizado in nomesCatalogo:
                raise ValueError("Há nomes duplicados no catálogo.")
            nomesCatalogo.add(nomeNormalizado)
            locaisValidados.append((local, categorias))
        return locaisValidados
    except (OSError, KeyError, TypeError, ValueError, ValidationError) as erro:
        raise CommandError(f"Catálogo inválido: {erro}") from erro


class Command(BaseCommand):
    help = "Adiciona atrativos reais de Paranaguá sem sobrescrever registros existentes."

    @transaction.atomic
    def handle(self, *args, **opcoes):
        locaisValidados = carregarCatalogo()
        nomesExistentes = {normalizarNome(nome) for nome in Atrativo.objects.values_list("nome", flat=True)}
        categoriasExistentes = {normalizarNome(categoria.titulo): categoria for categoria in Categoria.objects.order_by("id")}
        totalCriados = 0
        totalPreservados = 0
        for local, titulosCategorias in locaisValidados:
            nomeNormalizado = normalizarNome(local.nome)
            if nomeNormalizado in nomesExistentes:
                totalPreservados += 1
                self.stdout.write(f"Preservado: {local.nome}")
                continue
            categoriasLocal = []
            for titulo in titulosCategorias:
                tituloNormalizado = normalizarNome(titulo)
                categoria = categoriasExistentes.get(tituloNormalizado)
                if categoria is None:
                    categoria = Categoria.objects.create(titulo=titulo, tipo=TipoCategoria.LOCAL)
                    categoriasExistentes[tituloNormalizado] = categoria
                categoriasLocal.append(categoria)
            local.save()
            local.categorias.set(categoriasLocal)
            nomesExistentes.add(nomeNormalizado)
            totalCriados += 1
            self.stdout.write(f"Criado: {local.nome}")
        self.stdout.write(self.style.SUCCESS(
            f"Catálogo concluído: {totalCriados} locais criados; {totalPreservados} registros preservados."
        ))
