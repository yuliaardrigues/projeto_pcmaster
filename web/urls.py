from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Página inicial
    path('home/', views.home, name='home'),


    # Página de detalhes de um produto
    path('produto/<int:pk>/', views.produto, name='produto'),

    # Adicionar produto ao carrinho
    path('carrinho/', views.carrinho, name='carrinho'),
    # Adicionar produto aos favoritos
    path('favoritos/adicionar/<int:produto_id>/', views.adicionar_aos_favoritos, name='adicionar_aos_favoritos'),

    # Filtrar produtos por categoria
    
]
