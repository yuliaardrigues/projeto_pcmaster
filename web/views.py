from django.shortcuts import render, redirect
from .models import Produto, Categoria, Subcategoria

def home(request):
    produto = Produto.objects.all()
    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()
    return render(request, 'home/home.html', {'produtos':produto, 'categorias': categorias, 'subcategorias': subcategorias}) 

def produto(request):
    produto = Produto.objects.all()
    return render(request, 'products/produto.html', {'produtos':produto})

def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', [])
    if produto_id not in carrinho:
        carrinho.append(produto_id)
        request.session['carrinho'] = carrinho
    return redirect('home')  

def adicionar_aos_favoritos(request, produto_id):
    favoritos = request.session.get('favoritos', [])
    if produto_id not in favoritos:
        favoritos.append(produto_id)
        request.session['favoritos'] = favoritos
    return redirect('home') 

def detalhe_produto(request, produto_id):
    produto = Produto.objects.get(id=produto_id)
    return render(request, 'products/produto_detalhe.html', {'produto': produto})
