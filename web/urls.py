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

    path('finalizar_pedido/', views.finalizar_pedido, name='finalizar_pedido'), 

    path('favoritos/', views.favoritos, name='favoritos'),

    path('favoritos/remover/<int:produto_id>/', views.remover_dos_favoritos, name='remover_dos_favoritos'),
    path('carrinho/adicionar/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('chatbot/', views.chatbot, name='chatbot'),

]
