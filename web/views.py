from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria, Subcategoria
from django.http import HttpResponse


def home(request):
    produto = Produto.objects.all()
    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()
    return render(request, 'home/home.html', {
        'produtos': produto,
        'categorias': categorias,
        'subcategorias': subcategorias
    })


def produto(request, pk):
    produto = get_object_or_404(Produto, id=pk)
    
    return render(request, 'products/produto.html', {
        'produto': produto
    })


def todos_os_produtos(request):
    produtos = Produto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'products/todos.html', {
        'produtos': produtos,
        'categorias': categorias
    })


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


def produtos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    produtos = Produto.objects.filter(categoria=categoria)
    categorias = Categoria.objects.all()
    return render(request, 'home/home.html', {
        'produtos': produtos,
        'categorias': categorias,
        'categoria_selecionada': categoria
    })

