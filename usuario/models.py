from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='perfil')
    pontos = models.PositiveIntegerField(default=0)

    def __str__(self):
        if self.usuario:
            return self.usuario.username
        return f'Perfil sem usuário (ID: {self.id})'
