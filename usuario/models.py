from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='perfil')
    pontos = models.PositiveIntegerField(default=0)

    def __str__(self):
        if self.usuario:
            return self.usuario.username
        return f'Perfil sem usuário (ID: {self.id})'

    def get_badge(self):
        """Retorna o nome da badge de acordo com os pontos."""
        if self.pontos <= 100:
            return 'bronze'
        elif self.pontos <= 300:
            return 'prata'
        elif self.pontos <= 600:
            return 'ouro'
        else:
            return 'diamante'
