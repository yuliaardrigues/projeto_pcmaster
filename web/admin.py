from django.contrib import admin
from .models import Produto, Categoria, Carrinho, CarrinhoProduto, Pedido, Subcategoria


admin.site.register(Produto)
admin.site.register(Categoria)
admin.site.register(Carrinho)
admin.site.register(CarrinhoProduto)
admin.site.register(Pedido)
admin.site.register(Subcategoria)