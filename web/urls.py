from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Página inicial
    path('home/', views.home, name='home'),


    # Página de detalhes de um produto
    path('produto/<int:pk>/', views.produto, name='produto'),

    # Adicionar produto ao carrinho
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),

    # Adicionar produto aos favoritos
    path('favoritos/adicionar/<int:produto_id>/', views.adicionar_aos_favoritos, name='adicionar_aos_favoritos'),

    # Filtrar produtos por categoria
    path('categoria/<int:categoria_id>/', views.produtos_por_categoria, name='produtos_por_categoria'),
]
