from django.db import models
from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=200)
    imagem = models.ImageField(upload_to='categorias/', null=True, blank=True)

    def __str__(self):
        return self.nome

    
class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, default=1)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=250, default='', blank=True)
    preco = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos_thumb')
    nota = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def estrelas_cheias(self):
        if self.nota is None:
            return 0  # Retorna 0 se a nota for None
        return int(self.nota)

    def estrelas_meia(self):
        if self.nota is None:
            return 0  # Retorna 0 se a nota for None
        return 1 if self.nota - int(self.nota) >= 0.5 else 0
    # add sale

    sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    nota = models.FloatField(null=True, blank=True)



    def __str__(self):
        return self.nome
    
    @property
    def desconto_percentual(self):
        if self.preco > 0 and self.sale_price < self.preco:
            return int(((self.preco - self.sale_price) / self.preco) * 100)
        return 0
    
#carrinho de compras 
class Carrinho(models.Model):
    estado = models.CharField(choices=[("0", "aberto"), ("1", "Finalizado")], max_length=2)
    
    def __str__(self):
        return f"{self.usuario.nome} - {self.estado}"   
#itens dentro do carrinho de compras
class CarrinhoProduto(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='produtos')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantidade} {self.produto.nome}"
      
        
class Subcategoria(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    Produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='subcategorias', default=1)

    def __str__(self):
        return self.nome
    


class Pedido(models.Model):
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    data_pedido = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Pedido de {self.quantidade}x {self.produto.nome} em {self.data_pedido.strftime('%d/%m/%Y %H:%M')}"

