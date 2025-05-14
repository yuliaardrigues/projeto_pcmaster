from django.shortcuts import render
from .models import Produto, Categoria, Subcategoria

def home(request):
    produto = Produto.objects.all()
    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()
    return render(request, 'home/home.html', {'produtos':produto, 'categorias': categorias, 'subcategorias': subcategorias}) 

def produto(request):
    produto = Produto.objects.all()
    return render(request, 'products/produto.html', {'produtos':produto})