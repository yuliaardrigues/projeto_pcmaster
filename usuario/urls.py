from django.contrib import admin
from django.urls import path
from . import views
from .views import carrinho_view


urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('esqueci-senha/', views.esqueci_senha, name='esqueci_senha'),
    path('carrinho/', carrinho_view, name='carrinho'),
    path('rastrear-pedido/', views.rastrear_pedido, name='rastrear_pedido'), 
]
