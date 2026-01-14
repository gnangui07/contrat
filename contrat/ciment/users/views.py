from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import User


def home_view(request):
    """Page d'accueil - Redirige vers le dashboard si authentifié"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return redirect('users:login')


def activate_account(request, token):
    """Page d'activation du compte avec le token"""
    user = get_object_or_404(User, activation_token=token)
    
    # Vérifie si le token est encore valide
    if not user.is_token_valid():
        messages.error(request, "Ce lien d'activation a expiré. Veuillez contacter l'administrateur.")
        return redirect('users:login')
    
    # Vérifie si le compte est déjà activé
    if user.is_active:
        messages.info(request, "Votre compte est déjà activé. Vous pouvez vous connecter.")
        return redirect('users:login')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        temp_password = request.POST.get('temp_password')
        
        # Vérifie les identifiants
        if email != user.email:
            messages.error(request, "L'adresse email ne correspond pas.")
            return render(request, 'users/activate.html', {'user': user})
        
        if not user.check_temporary_password(temp_password):
            messages.error(request, "Le mot de passe temporaire est incorrect.")
            return render(request, 'users/activate.html', {'user': user})
        
        # Redirige vers la page de confirmation pour créer le nouveau mot de passe
        return redirect('users:confirm_password', token=token)
    
    return render(request, 'users/activate.html', {'user': user})


def confirm_password(request, token):
    """Page de confirmation et création du nouveau mot de passe"""
    user = get_object_or_404(User, activation_token=token)
    
    # Vérifie si le token est encore valide
    if not user.is_token_valid():
        messages.error(request, "Ce lien d'activation a expiré. Veuillez contacter l'administrateur.")
        return redirect('users:login')
    
    # Vérifie si le compte est déjà activé
    if user.is_active:
        messages.info(request, "Votre compte est déjà activé. Vous pouvez vous connecter.")
        return redirect('users:login')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation des mots de passe
        if not new_password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, 'users/confirm_password.html', {'user': user})
        
        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'users/confirm_password.html', {'user': user})
        
        if len(new_password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return render(request, 'users/confirm_password.html', {'user': user})
        
        # Définit le nouveau mot de passe et active le compte
        user.set_password(new_password)
        user.activate_account()
        
        messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect('users:login')
    
    return render(request, 'users/confirm_password.html', {'user': user})


def login_view(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('users:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authentification
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Bienvenue {user.get_full_name()} !")
                
                # Redirige vers la page demandée ou la page d'accueil
                next_url = request.GET.get('next', 'users:home')
                return redirect(next_url)
            else:
                messages.error(request, "Votre compte n'est pas encore activé. Veuillez vérifier votre email.")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    response = redirect('users:login')
    # Désactive le cache pour empêcher le retour en arrière
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

