from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Contract(models.Model):
    """Modèle pour les contrats"""
    
    TYPES = [
        ('capex', 'CAPEX'),
        ('opex', 'OPEX'),
        ('service', 'Service'),
        ('travaux', 'Travaux'),
        ('it', 'IT'),
    ]
    
    STATUSES = [
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('rejected', 'Rejeté'),
        ('suspended', 'Suspendu'),
    ]
    
    DEVISES = [
        ('XOF', 'XOF'),
        ('EUR', 'EUR'),
        ('USD', 'USD'),
        ('GBP', 'GBP'),
    ]

    # Nouvelles constantes
    TYPE_RENOUVELLEMENT = [
        ('tacite', 'Tacite'),
        ('accord_express', 'Par accord express'),
        ('avenant', 'Avenant'),
    ]
    # Liste de durées autorisées (1 à 5 ans)
    DUREES = [(i, str(i)) for i in range(1, 6)]
    
    numero = models.CharField(max_length=100, unique=True)
    objet = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPES)
    # Nouveau: Type de contrat (texte libre, à convertir en choices si besoin)
    type_contrat = models.CharField(max_length=100, verbose_name="Type de contrat", blank=True, null=True)
    # Nouveau: Type d'activité (texte libre saisi par l'utilisateur)
    type_activite = models.CharField(max_length=100, verbose_name="Type d'activité", blank=True, null=True)
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    devise = models.CharField(max_length=10, choices=DEVISES, default='XOF')
    
    date_signature = models.DateField()
    date_effet = models.DateField()
    date_expiry = models.DateField()
    preavis = models.IntegerField(default=90, help_text="Nombre de jours avant l'échéance")
    # Nouveau: Durée du contrat (1 à 5 ans)
    duree_contrat = models.PositiveSmallIntegerField(choices=DUREES, verbose_name="Durée du contrat (années)", blank=True, null=True)
    # Nouveau: Type de renouvellement
    type_renouvellement = models.CharField(max_length=20, choices=TYPE_RENOUVELLEMENT, blank=True, null=True, verbose_name="Type de renouvellement")
    
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.CASCADE, related_name='contracts')
    status = models.CharField(max_length=50, choices=STATUSES, default='pending')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contracts_created')
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts_validated')
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.numero} - {self.objet}"
    
    def jours_avant_echeance(self):
        """Calcule le nombre de jours avant l'échéance"""
        today = timezone.now().date()
        delta = self.date_expiry - today
        return delta.days
    
    def est_a_renouveler(self):
        """Vérifie si le contrat doit être renouvelé"""
        jours = self.jours_avant_echeance()
        return self.status == 'active' and 0 <= jours <= self.preavis
