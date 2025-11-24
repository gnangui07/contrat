from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    """Formulaire de création d'utilisateur"""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'direction', 'phone', 'photo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs obligatoires
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Administration personnalisée pour le modèle User"""
    
    form = UserCreationForm
    add_form = UserCreationForm
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'direction', 'is_active', 'activation_status', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'role', 'direction', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'direction']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'photo')
        }),
        ('Rôle et organisation', {
            'fields': ('role', 'direction')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Informations d\'activation', {
            'fields': ('activation_token', 'token_created_at', 'temporary_password'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'role', 'direction', 'photo'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'activation_token', 'token_created_at', 'temporary_password']
    
    def get_fieldsets(self, request, obj=None):
        """Utilise add_fieldsets lors de la création"""
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    def activation_status(self, obj):
        """Affiche le statut d'activation avec icône"""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Activé</span>')
        elif obj.activation_token:
            return format_html('<span style="color: orange;">⏳ En attente</span>')
        else:
            return format_html('<span style="color: red;">✗ Non activé</span>')
    activation_status.short_description = 'Statut'
    
    def save_model(self, request, obj, form, change):
        """Surcharge pour envoyer l'email d'activation lors de la création"""
        is_new = obj.pk is None
        
        if is_new:
            # Génère le mot de passe temporaire et le token
            temp_password = obj.generate_temporary_password()
            obj.generate_activation_token()
            
            # Sauvegarde l'utilisateur
            super().save_model(request, obj, form, change)
            
            # Envoie l'email d'activation
            self.send_activation_email(obj, temp_password, request)
            
            # Message de succès
            self.message_user(
                request,
                f"Utilisateur créé avec succès. Email d'activation envoyé à {obj.email}",
                level='success'
            )
        else:
            super().save_model(request, obj, form, change)
    
    def send_activation_email(self, user, temp_password, request):
        """Envoie l'email d'activation à l'utilisateur"""
        try:
            # Construction du lien d'activation avec SITE_URL
            activation_path = reverse('users:activate', kwargs={'token': user.activation_token})
            activation_url = f"{settings.SITE_URL}{activation_path}"
            
            # Sujet de l'email
            subject = f"Activation de votre compte - {settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'MTN CI'}"
            
            # Corps de l'email en HTML
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #FFCC00; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; }}
                    .credentials {{ background-color: #fff; padding: 15px; border-left: 4px solid #FFCC00; margin: 20px 0; }}
                    .button {{ display: inline-block; padding: 12px 30px; background-color: #FFCC00; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0; color: #000;">Bienvenue !</h1>
                    </div>
                    <div class="content">
                        <p>Bonjour <strong>{user.first_name} {user.last_name}</strong>,</p>
                        
                        <p>Votre compte a été créé avec succès sur la plateforme de gestion de projets MTN Côte d'Ivoire.</p>
                        
                        <div class="credentials">
                            <p><strong>Vos identifiants temporaires :</strong></p>
                            <p>📧 <strong>Email :</strong> {user.email}</p>
                            <p>🔑 <strong>Mot de passe temporaire :</strong> {temp_password}</p>
                        </div>
                        
                        <p>Pour activer votre compte, veuillez cliquer sur le bouton ci-dessous :</p>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="{activation_url}" class="button">Activer mon compte</a>
                        </p>
                        
                        <p style="font-size: 12px; color: #666;">
                            Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :<br>
                            <a href="{activation_url}">{activation_url}</a>
                        </p>
                        
                        <p><strong>⚠️ Important :</strong></p>
                        <ul>
                            <li>Ce lien est valide pendant 48 heures</li>
                            <li>Vous devrez créer un nouveau mot de passe sécurisé lors de l'activation</li>
                            <li>Ne partagez jamais vos identifiants</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>© 2025 MTN Côte d'Ivoire - Plateforme de Gestion de Projets</p>
                        <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Corps de l'email en texte brut (fallback)
            plain_message = f"""
            Bonjour {user.first_name} {user.last_name},
            
            Votre compte a été créé avec succès sur la plateforme de gestion de projets MTN Côte d'Ivoire.
            
            Vos identifiants temporaires :
            Email : {user.email}
            Mot de passe temporaire : {temp_password}
            
            Pour activer votre compte, cliquez sur ce lien :
            {activation_url}
            
            Ce lien est valide pendant 48 heures.
            Vous devrez créer un nouveau mot de passe sécurisé lors de l'activation.
            
            © 2025 MTN Côte d'Ivoire
            """
            
            # Envoi de l'email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
        except Exception as e:
            # Log l'erreur mais ne bloque pas la création
            print(f"Erreur lors de l'envoi de l'email : {str(e)}")
            # En production, utiliser un logger approprié
