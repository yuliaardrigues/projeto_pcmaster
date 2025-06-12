from django.shortcuts import render, redirect, get_object_or_404
from .models import Subcategoria, Pedido
from usuario.models import Perfil
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import requests
from django.shortcuts import render
import watson
import ipdb
from django.db.models import Q
from web.models import Produto, Categoria

@csrf_exempt
def chatbot(request):
    if request.method == "GET":
        return render(request, "chatbot.html")  # renderiza a página HTML do chatbot

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            resposta = gerar_resposta_ia(user_message)


            return JsonResponse({"reply": resposta})
        except Exception as e:
            return JsonResponse({"reply": "Erro ao processar a mensagem."}, status=500)

    else:
        return JsonResponse({"error": "Método não permitido."}, status=405)

import requests

GROQ_API_KEY = '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'

def gerar_resposta_ia(pergunta, historico=None):
    try:
        produtos = Produto.objects.all()
        contexto_produtos = "Estes são os produtos disponíveis:\n\n"
        for p in produtos:
            contexto_produtos += (
                f"Nome: {p.nome}\n"
                f"Descrição: {p.descricao}\n"
                f"Preço: R${p.preco:.2f}\n"
                f"Em promoção: {'Sim, por R$'+str(p.sale_price) if p.sale else 'Não'}\n"
                f"Nota: {p.nota}\n"
                f"Link: /produto/{p.id}/\n\n"
            )

        prompt_sistema = (
            "Você é um especialista em produtos de informática. "
            "Só responda com base nas informações dos produtos listados. "
            "Se o usuário pedir mais detalhes sobre um produto mencionado anteriormente, mantenha o contexto da conversa.\n\n"
            + contexto_produtos
        )

        mensagens = [{"role": "system", "content": prompt_sistema}]
        if historico:
            mensagens += historico
        mensagens.append({"role": "user", "content": pergunta})

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": mensagens,
                "temperature": 0.7
            },
            timeout=60
        )

        if response.status_code != 200:
            print("Erro:", response.status_code, response.text)
            return "Erro ao acessar o assistente. Tente novamente mais tarde."

        resposta = response.json()["choices"][0]["message"]["content"]
        return resposta

    except Exception as e:
        print("Erro:", e)
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

from django.db.models import Q

def produto(request, pk):
    produto = get_object_or_404(Produto, id=pk)
    estrelas = produto.get_estrelas()

    return render(request, 'products/produto.html', {
        'produto': produto,
        'estrelas': estrelas,
    })


def todos_os_produtos(request):
    search = request.GET.get('q', '')
    categorias = Categoria.objects.all()
    produtos = Produto.objects.all()

    if search:
        produtos = produtos.filter(nome__icontains=search)

    context = {
        'produtos': produtos,
        'categorias': categorias,
        'search': search,
    }
    return render(request, 'products/todos.html', context)


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

def produtos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    produtos = Produto.objects.filter(categoria=categoria)
    return render(request, 'web/produtos_por_categoria.html', {
        'categoria': categoria,
        'produtos': produtos
    })


def conferir_pontos(request):
    pontos = 0
    # Busca pontos do perfil do usuário, criando perfil se não existir
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        perfil = Perfil.objects.create(usuario=request.user)
    
    pontos = perfil.pontos

    # Definindo patente e bonificação com base na pontuação
    if pontos >= 1000:
        patente = "Diamante"
        bonificacao = "Frete grátis + 20% de desconto em qualquer produto."
    elif pontos >= 500:
        patente = "Ouro"
        bonificacao = "15% de desconto em headsets e cadeiras gamers."
    elif pontos >= 100:
        patente = "Prata"
        bonificacao = "10% de desconto em teclados e mouses."
    else:
        patente = "Bronze"
        bonificacao = "5% de desconto em acessórios básicos (mousepads, cabos, etc)."

    context = {
        'pontos': pontos,
        'patente': patente,
        'bonificacao': bonificacao,
    }
    return render(request, 'conferir_pontos.html', context)
