from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('esqueci-senha/', views.esqueci_senha, name='esqueci_senha'),

]
