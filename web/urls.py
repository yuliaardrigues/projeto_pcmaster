from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('produto/', views.produto, name='produto'),
    path('produto/<int:produto_id>/', views.detalhe_produto, name='detalhe_produto'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('favoritos/adicionar/<int:produto_id>/', views.adicionar_aos_favoritos, name='adicionar_aos_favoritos'),
    path('categoria/<int:categoria_id>/', views.produtos_por_categoria, name='produtos_por_categoria'),
]


