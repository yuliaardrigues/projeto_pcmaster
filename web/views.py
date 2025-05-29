from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria, Subcategoria, Carrinho, CarrinhoProduto
from django.http import HttpResponse, Http404


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
    estrelas_cheias = produto.estrelas_cheias()  # Correto, função!
    estrelas_meia = produto.estrelas_meia()      # Correto, função!
    nota_restante = 5 - estrelas_cheias - estrelas_meia

    return render(request, 'products/produto.html', {
        'produto': produto,
        'estrelas_cheias': estrelas_cheias,
        'estrelas_meia': estrelas_meia,
        'nota_restante': nota_restante,
    })



def todos_os_produtos(request):
    produtos = Produto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'products/todos.html', {
        'produtos': produtos,
        'categorias': categorias
    })




def adicionar_aos_favoritos(request, produto_id):
    favoritos = request.session.get('favoritos', [])
    if produto_id not in favoritos:
        favoritos.append(produto_id)
        request.session['favoritos'] = favoritos
    return redirect('home')

def carrinho(request):
    if request.method == 'POST':
        # Adicionar produto ao carrinho via POST
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantity', 1))
    else:
        # Adicionar produto ao carrinho via GET
        produto_id = request.GET.get('produto_id')
        quantidade = int(request.GET.get('quantidade', 1))

    if produto_id:
        try:
            produto_id = int(produto_id)  # Certifique-se de que é um número
        except ValueError:
            return redirect('carrinho')  # Redirecione se o produto_id for inválido

        carrinho = request.session.get('carrinho', {})
        produto_id = str(produto_id)

        if produto_id in carrinho:
            carrinho[produto_id] += quantidade
        else:
            carrinho[produto_id] = quantidade

        request.session['carrinho'] = carrinho
        return redirect('carrinho')

    # Exibir os itens do carrinho
    carrinho = request.session.get('carrinho', {})
    itens = []
    subtotal = 0

    for pid, qtd in carrinho.items():
        try:
            produto = get_object_or_404(Produto, id=pid)
        except ValueError:
            continue  # Pule IDs inválidos no carrinho

        subtotal += produto.preco * qtd
        itens.append({
            'produto': produto,
            'quantidade': qtd,
            'subtotal': produto.preco * qtd,
        })

    contexto = {
        'carrinho': {
            'itens': itens,
            'subtotal': subtotal,
            'desconto': 0,
            'total': subtotal,
        }
    }
    return render(request, 'products/carrinho.html', contexto)

