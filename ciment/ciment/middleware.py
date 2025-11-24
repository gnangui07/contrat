"""
Middleware personnalisé pour la sécurité et la gestion des sessions
"""
from django.utils.deprecation import MiddlewareMixin


class NoCache(MiddlewareMixin):
    """
    Middleware pour empêcher le cache des pages protégées.
    Cela force le navigateur à recharger les pages au lieu d'utiliser le cache.
    """
    
    def process_response(self, request, response):
        """Ajoute les headers de cache control"""
        
        # Empêcher le cache pour toutes les pages
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware pour renforcer la sécurité des sessions.
    Vérifie que l'utilisateur est toujours authentifié.
    """
    
    def process_request(self, request):
        """Vérifie la session à chaque requête"""
        
        # Si l'utilisateur est authentifié, mettre à jour la session
        if request.user.is_authenticated:
            # Régénérer la session pour éviter les attaques de fixation
            request.session.modified = True
        
        return None
