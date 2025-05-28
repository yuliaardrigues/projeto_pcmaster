from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.db.models.signals import post_save
from django.dispatch import receiver


def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if len(username.strip()) == 0 or len(email.strip()) == 0:
            return redirect('cadastro')
            

        if not password == confirm_password:
            messages.info(request, 'As senhas não coincidem.')
            return redirect('cadastro')
        
        if len(password) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            return redirect('cadastro')
        

        
        if User.objects.filter(email=email).exists():
            messages.error(request,'Esse nome de usuário já existe.')
            return redirect('cadastro')
        
        usuario = User.objects.create_user(username=username, email=email, password=password)
        usuario.save()
        messages.success(request, 'Usuário cadastrado com sucesso.')
        

        return redirect('login')

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            auth_login(request, user)
            return redirect('/home/')
        messages.error(request, 'Usuário ou senha inválidos.')
        return redirect('login')
    
def esqueci_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Aqui você implementaria envio de e-mail ou lógica de recuperação
        messages.success(request, 'Se o e-mail existir, as instruções foram enviadas.')
        return redirect('login')  # Redireciona de volta ao login
    return render(request, 'esqueci_senha.html')
    
        
def carrinho_view(request):
    return render(request, 'usuario/carrinho.html')
 

def rastrear_pedido(request):
    return render(request, 'usuario/rastrear_pedido.html')
