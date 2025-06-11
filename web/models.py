from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from math import floor
from django.utils.text import slugify


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    # slug = models.SlugField(unique=True, blank=True)  # pode ficar em branco para gerar automaticamente

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Subcategoria(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, default=1)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=250, default='', blank=True)
    preco = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos_thumb')
    nota = models.FloatField(null=True, blank=True)
    sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def get_estrelas(self):
        return {
            'estrelas_cheias': self.estrelas_cheias(),
            'estrelas_meia': self.estrelas_meia(),
            'nota_restante': self.nota_restante(),
        }

    def estrelas_cheias(self):
        if self.nota:
            return int(floor(self.nota))
        return 0

    def estrelas_meia(self):
        if self.nota:
            return (self.nota - floor(self.nota)) >= 0.5
        return False

    def nota_restante(self):
        total = 5
        cheias = self.estrelas_cheias()
        meia = 1 if self.estrelas_meia() else 0
        return total - cheias - meia

    def __str__(self):
        return self.nome

    @property
    def desconto_percentual(self):
        if self.preco > 0 and self.sale_price < self.preco:
            return int(((self.preco - self.sale_price) / self.preco) * 100)
        return 0


class Carrinho(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(choices=[("0", "aberto"), ("1", "finalizado")], max_length=2)

    def __str__(self):
        return f"{self.usuario} - {self.estado}"


class CarrinhoProduto(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='produtos')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome}"


class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, default=1)
    quantidade = models.IntegerField(default=1)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    data_pedido = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Pedido de {self.quantidade}x {self.produto.nome} em {self.data_pedido.strftime('%d/%m/%Y %H:%M')}"
