from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required


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

        # Exemplo simples: verificar se email existe, enviar código etc.
        if email:
            # Lógica para enviar código aqui...

            # Depois redireciona para mudar senha
            return redirect('mudar_senha')
        else:
            messages.error(request, "Informe um email válido.")
            # Aqui precisa retornar render para mostrar a página com mensagem
            return render(request, 'esqueci_senha.html')

    # Se for GET, apenas exibe o formulário
    return render(request, 'esqueci_senha.html')


        
def mudar_senha(request):
    if request.method == 'POST':
        codigo_enviado = request.POST.get('codigo')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        codigo_salvo = request.session.get('codigo_verificacao')
        email_usuario = request.session.get('email_recuperacao')

        if not (codigo_enviado and nova_senha and confirmar_senha):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('mudar_senha')

        if codigo_enviado != codigo_salvo:
            messages.error(request, 'Código de verificação inválido.')
            return redirect('mudar_senha')

        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('mudar_senha')

        try:
            user = User.objects.get(email=email_usuario)
            user.password = make_password(nova_senha)
            user.save()

            # Remove dados da sessão
            request.session.pop('codigo_verificacao', None)
            request.session.pop('email_recuperacao', None)

            messages.success(request, 'Senha alterada com sucesso! Faça login com sua nova senha.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return redirect('mudar_senha')

    return render(request, 'mudar_senha.html')

@login_required
def perfil(request):
    perfil = request.user.perfil  
    badge = perfil.get_badge()    

    return render(request, 'perfil.html', {
        'perfil': perfil,
        'badge': badge,
    })