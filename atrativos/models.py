from django.db import models


class TipoCategoria(models.TextChoices):
    LOCAL = 'local', 'Local'
    EVENTO = 'evento', 'Evento'
    AMBOS = 'ambos', 'Ambos'


class Categoria(models.Model):
    titulo = models.CharField(max_length=45)
    ativo = models.BooleanField(default=True)
    tipo = models.CharField(
        max_length=20,
        choices=TipoCategoria.choices,
        default=TipoCategoria.AMBOS,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"


class Atrativo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    endereco = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    ativo = models.BooleanField(default=True)
    valor_entrada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    categorias = models.ManyToManyField(Categoria, related_name='atrativos', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Atrativo'
        verbose_name_plural = 'Atrativos'

    def __str__(self):
        return self.nome


class Local(Atrativo):
    horario_abertura = models.TimeField()
    horario_fechamento = models.TimeField()

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'


class Evento(Atrativo):
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'


class AtrativoImagem(models.Model):
    atrativo = models.ForeignKey(Atrativo, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='atrativos/')
    imagem_capa = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem do Atrativo'
        verbose_name_plural = 'Imagens dos Atrativos'
        ordering = ['-imagem_capa', '-id']

    def __str__(self):
        return f"Imagem de {self.atrativo.nome}"
