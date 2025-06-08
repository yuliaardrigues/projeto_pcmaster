from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria, Subcategoria, Pedido
from usuario.models import Perfil
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import requests

@csrf_exempt
def chatbot(request):
    if request.method == "GET":
        return render(request, "chatbot.html")  # renderiza a página HTML do chatbot

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            # Aqui você integraria seu modelo de linguagem ou lógica de resposta
            resposta = gerar_resposta_ia(user_message)


            return JsonResponse({"reply": resposta})
        except Exception as e:
            return JsonResponse({"reply": "Erro ao processar a mensagem."}, status=500)

    else:
        return JsonResponse({"error": "Método não permitido."}, status=405)

import requests

GROQ_API_KEY = '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'

def gerar_resposta_ia(pergunta):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",  # ou "llama3-70b-8192" se quiser o modelo maior
                "messages": [
                    {"role": "system", "content": "Você é um especialista em periféricos de computador."},
                    {"role": "user", "content": pergunta}
                ],
                "temperature": 0.7
            },
            timeout=60
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("Erro ao consultar Groq:", e)
        return "Erro ao acessar o assistente. Tente novamente mais tarde."



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
    estrelas = produto.get_estrelas()

    return render(request, 'products/produto.html', {
        'produto': produto,
        'estrelas': estrelas,
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

        if action == 'decrement':
          carrinho[produto_id] = max(carrinho[produto_id] - 1, 0)
          if carrinho[produto_id] == 0:
            del carrinho[produto_id]

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


@login_required  # remova se quiser permitir checkout sem login
def finalizar_pedido(request):

    carrinho = request.session.get("carrinho", {})

    if not carrinho:
        return redirect("carrinho")

    itens, subtotal, desconto = [], 0, 0  # implemente cupons no futuro

    # ----- monta lista de itens -----
    for pid, qtd in carrinho.items():
        try:
            pid_int = int(pid)
        except (ValueError, TypeError):
            continue  # ignora IDs inválidos

        produto = get_object_or_404(Produto, id=pid_int)

        subtotal_item = produto.preco * qtd
        subtotal += subtotal_item
        itens.append({
            "produto": produto,
            "quantidade": qtd,
            "subtotal": subtotal_item,
        })

    total = subtotal - desconto

    # ----- grava pedido -----
    if request.method == "POST":
        for item in itens:
            Pedido.objects.create(
                usuario=request.user,  # adicione este FK ao model
                produto=item["produto"],
                quantidade=item["quantidade"],
                valor_total=item["subtotal"],
                status=True,
                data_pedido=timezone.now(),
            )

        # pontos de fidelidade (1 ponto por R$ 10,00)
        try:
            perfil = request.user.perfil
        except Perfil.DoesNotExist:
            perfil = Perfil.objects.create(usuario=request.user)

        perfil.pontos += int(total / 10)
        perfil.save()

        # limpa carrinho
        request.session["carrinho"] = {}
        request.session.modified = True

        return redirect("home")

    # ----- exibe página -----
    contexto = {
        "itens": itens,
        "subtotal": subtotal,
        "desconto": desconto,
        "total": total,
    }
    return render(request, "web/finalizar_pedido.html", contexto)


def favoritos(request):
    favoritos_ids = request.session.get('favoritos', [])
    produtos_favoritos = Produto.objects.filter(id__in=favoritos_ids)
    return render(request, 'web/favoritos.html', {'produtos': produtos_favoritos})

def remover_dos_favoritos(request, produto_id):
    favoritos = request.session.get('favoritos', [])
    if produto_id in favoritos:
        favoritos.remove(produto_id)
        request.session['favoritos'] = favoritos
    return redirect('favoritos') 

def adicionar_ao_carrinho(request):
    produto_id = request.POST.get('produto_id')
    quantidade = int(request.POST.get('quantidade', 1))

    carrinho = request.session.get('carrinho', {})

    if produto_id:
        produto_id = str(produto_id)
        carrinho[produto_id] = carrinho.get(produto_id, 0) + quantidade
        request.session['carrinho'] = carrinho

    return redirect('carrinho')