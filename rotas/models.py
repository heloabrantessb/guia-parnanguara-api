from django.db import models
from usuarios.models import Usuario
from atrativos.models import Atrativo


class Rota(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='rotas')
    titulo = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Rota'
        verbose_name_plural = 'Rotas'

    def __str__(self):
        return f"{self.titulo} - ({self.usuario.email})"


class RotaAtrativo(models.Model):
    rota = models.ForeignKey(Rota, on_delete=models.CASCADE, related_name='itens')
    atrativo = models.ForeignKey(Atrativo, on_delete=models.CASCADE, related_name='rotas')
    ordem = models.PositiveIntegerField()

    class Meta:
        ordering = ['ordem']
        unique_together = ('rota', 'atrativo')
        verbose_name = 'Atrativo do Roteiro'
        verbose_name_plural = 'Atrativos dos Roteiros'

    def __str__(self):
        return f"{self.rota.titulo} - Item {self.ordem}: {self.atrativo.nome}"
