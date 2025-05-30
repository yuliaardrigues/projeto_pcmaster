from django.db import models
from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pontos = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.pontos} pontos"
    
    