from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria, Subcategoria, Pedido
from django.views.decorators.http import require_http_methods

def home(request):
    produtos = Produto.objects.all()
    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()
    return render(request, 'home/home.html', {
        'produtos': produtos,
        'categorias': categorias,
        'subcategorias': subcategorias
    })

def produto(request, pk):
    produto = get_object_or_404(Produto, id=pk)
    estrelas_cheias = produto.estrelas_cheias()
    estrelas_meia = produto.estrelas_meia()
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


@require_http_methods(["GET", "POST"])
def carrinho(request):
    carrinho = request.session.get('carrinho', {})

    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        action = request.POST.get('action')

        if not produto_id:
            return redirect('carrinho')

        produto = get_object_or_404(Produto, id=produto_id)
        produto_id = str(produto_id)

        # Inicializa no carrinho caso não exista
        if produto_id not in carrinho:
            carrinho[produto_id] = 0

        if action == 'increment':
            carrinho[produto_id] += 1

        elif action == 'decrement':
            if carrinho[produto_id] > 1:
                carrinho[produto_id] -= 1
            else:
                carrinho[produto_id] = 1

        elif action == 'update':
            try:
                quantidade = int(request.POST.get('quantidade', 1))
                if quantidade < 1:
                    quantidade = 1
                carrinho[produto_id] = quantidade
            except ValueError:
                pass

        elif action == 'remove':
            if produto_id in carrinho:
                del carrinho[produto_id]

        request.session['carrinho'] = carrinho
        return redirect('carrinho')

    # GET: Exibir carrinho
    itens = []
    subtotal = 0
    for pid, qtd in carrinho.items():
        try:
            produto = get_object_or_404(Produto, id=pid)
        except ValueError:
            continue
        subtotal_item = produto.preco * qtd
        subtotal += subtotal_item
        itens.append({
            'produto': produto,
            'quantidade': qtd,
            'subtotal': subtotal_item,
        })

    desconto = 0  # Ajuste para seu sistema de cupons
    total = subtotal - desconto

    contexto = {
        'carrinho': {
            'itens': itens,
            'subtotal': subtotal,
            'desconto': desconto,
            'total': total,
        }
    }
    return render(request, 'products/carrinho.html', contexto)


def finalizar_pedido(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        return redirect('carrinho')

    itens = []
    subtotal = 0
    desconto = 0  # Pode aplicar cupom

    for pid, qtd in carrinho.items():
        try:
            produto = get_object_or_404(Produto, id=pid)
        except ValueError:
            continue

        subtotal_item = produto.preco * qtd
        subtotal += subtotal_item
        itens.append({
            'produto': produto,
            'quantidade': qtd,
            'subtotal': subtotal_item,
        })

    total = subtotal - desconto

    contexto = {
        'itens': itens,
        'subtotal': subtotal,
        'desconto': desconto,
        'total': total,
    }

    if request.method == 'POST':
        # Criar pedidos
        for item in itens:
            Pedido.objects.create(
                produto=item['produto'],
                quantidade=item['quantidade'],
                valor_total=item['subtotal'],
                status=True
            )
        
        # Adicionar pontos ao perfil do usuário autenticado
        if request.user.is_authenticated:
            perfil = request.user.perfil
            perfil.pontos += 10  
            perfil.save()

        # Limpar carrinho
        request.session['carrinho'] = {}
        return redirect('home') 

    return render(request, 'web/finalizar_pedido.html', contexto)

def favoritos(request):
    favoritos_ids = request.session.get('favoritos', [])
    produtos_favoritos = Produto.objects.filter(id__in=favoritos_ids)
    return render(request, 'web/favoritos.html', {'produtos': produtos_favoritos})

def remover_dos_favoritos(request, produto_id):
    favoritos = request.session.get('favoritos', [])
    if produto_id in favoritos:
        favoritos.remove(produto_id)
        request.session['favoritos'] = favoritos
    return redirect('favoritos')  # Redireciona de volta para a página de favoritos
