from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return self.nome

    
class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos_thumb')

    def __str__(self):
        return self.nome
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
    

class Pedido(models.Model):
        data_pedido = models.DateTimeField(auto_now_add=True)
        status = models.CharField(choices=[("0", "Pendente"), ("1", "Enviado"), ("2", "Entregue")], max_length=2)
        valor_total = models.DecimalField(max_digits=10, decimal_places=2)

        def __str__(self):
            return f"Pedido {self.id} - {self.usuario.nome}"