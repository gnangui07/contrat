from django.db import models
from django.db.models import Avg
from decimal import Decimal

class Banque(models.Model):
    """Modèle pour stocker les informations des banques"""
    nom = models.CharField(max_length=255, verbose_name="Nom de la banque")
    sigle = models.CharField(max_length=50, verbose_name="Sigle")
    code_banque = models.CharField(max_length=5, verbose_name="Code banque (5 chiffres)", blank=True, null=True)
    code_bic = models.CharField(max_length=11, verbose_name="Code BIC/SWIFT", blank=True, null=True)
    iban_prefix = models.CharField(max_length=4, default="CI93", verbose_name="Préfixe IBAN")
    adresse = models.TextField(verbose_name="Adresse principale", blank=True, null=True)
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    site_web = models.URLField(verbose_name="Site web", blank=True, null=True)
    
    class Meta:
        verbose_name = "Banque"
        verbose_name_plural = "Banques"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.sigle})"


class Supplier(models.Model):
    # Informations Générales
    nom_complet_organisation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Nom complet de l'organisation",
    )

    TYPE_CHOICES = [
        ('Local', 'Local'),
        ('Foreign', 'Foreign'),
    ]
    type_fournisseur = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type (Local/Foreign)")

    TYPE_ORGANISATION_CHOICES = [
        ('SA', 'SA'),
        ('SARL', 'SARL'),
        ('SUARL', 'SUARL'),
        ('GIE', 'GIE'),
        ('SNC', 'SNC'),
        ('SCS', 'SCS'),
        ('SCA', 'SCA'),
        ('SCOP', 'SCOP'),
        ('Association', 'Association'),
        ('Autre', 'Autre'),
    ]
    type_organisation = models.CharField(max_length=50, choices=TYPE_ORGANISATION_CHOICES, verbose_name="Type d'organisation")

    date_enregistrement = models.DateField(verbose_name="Date d'enregistrement")
    adresse_physique = models.TextField(verbose_name="Adresse physique complète")
    adresse_siege_social = models.TextField(blank=True, null=True, verbose_name="Adresse du siège social (si différente)")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    email = models.EmailField(verbose_name="Adresse électronique")
    site_web = models.URLField(blank=True, null=True, verbose_name="Site web (si existant)")

    # Représentant Légal
    nom_representant_legal = models.CharField(max_length=255, verbose_name="Nom du Représentant Légal")
    fonction_representant = models.CharField(max_length=255, verbose_name="Fonction")

    # Personne de contact
    personne_contact = models.CharField(max_length=255, verbose_name="Personne de contact pour les demandes de renseignements")
    telephone_contact = models.CharField(max_length=20, verbose_name="Phone")
    email_contact = models.EmailField(verbose_name="e-mail")

    # Documents légaux
    registre_commerce = models.CharField(max_length=255, verbose_name="Registre de Commerce")
    numero_compte_contribuable = models.CharField(max_length=255, verbose_name="Numéro compte contribuable")
    attestation_regularite_fiscale = models.CharField(max_length=255, verbose_name="Attestation de régularité fiscale")
    numero_cnps = models.CharField(max_length=255, verbose_name="Numéro CNPS")

    # Informations Financières - Remplacé par ForeignKey
    banque_reference = models.ForeignKey(
        Banque, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Banque (référence)"
    )
    banque = models.CharField(max_length=255, verbose_name="Banque (texte libre)", blank=True, null=True)
    agence = models.CharField(max_length=255, verbose_name="Agence")
    iban = models.CharField(max_length=28, verbose_name="IBAN (28 positions pour les Locaux)")
    bic_swift = models.CharField(max_length=11, blank=True, null=True, verbose_name="BICCODE/SWIFT (obligatoire pour Foreign Suppliers)")

    MODALITE_PAIEMENT_CHOICES = [
        ('Net 30', 'Net 30'),
        ('Net 60', 'Net 60'),
        ('Net 90', 'Net 90'),
    ]
    modalite_paiement = models.CharField(max_length=10, choices=MODALITE_PAIEMENT_CHOICES, verbose_name="Modalité de règlement")

    # Branche d'activité
    TYPE_CATEGORIE_CHOICES = [
        ('Biens', 'Biens'),
        ('Services', 'Services'),
        ('Autres', 'Autres'),
    ]
    type_categorie = models.CharField(max_length=20, choices=TYPE_CATEGORIE_CHOICES, verbose_name="Type Catégorie (Biens,Services, Autres…)")

    CATEGORIE_CHOICES = [
        ('Fournitures générales de bureau et papeterie', 'Fournitures générales de bureau et papeterie'),
        ("Fourniture générale de matériel promotionnel", "Fourniture générale de matériel promotionnel"),
        ("Fourniture générale de matériel d'entretien", "Fourniture générale de matériel d'entretien"),
        ('Fourniture de boissons et de snacks', 'Fourniture de boissons et de snacks'),
        ('Fournitures médicales et consommables', 'Fournitures médicales et consommables'),
        ('Appareils informatiques', 'Appareils informatiques'),
        # Ajouter d'autres catégories depuis l'onglet "catégorie achat"
    ]
    categorie = models.CharField(max_length=255, choices=CATEGORIE_CHOICES, verbose_name="Catégorie")
    description_categorie = models.TextField(verbose_name="Description Catégorie")

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom_complet_organisation']

    def __str__(self):
        return self.nom_complet_organisation

    def save(self, *args, **kwargs):
        # Si une banque de référence est sélectionnée, remplir automatiquement les champs
        if self.banque_reference:
            self.banque = self.banque_reference.nom
            # Si c'est un fournisseur local, préfixer l'IBAN
            if self.type_fournisseur == 'Local' and self.iban and not self.iban.startswith('CI'):
                self.iban = f"CI93{self.iban}"
            # Si BIC/SWIFT est vide, utiliser celui de la banque
            if not self.bic_swift and self.banque_reference.code_bic:
                self.bic_swift = self.banque_reference.code_bic
        super().save(*args, **kwargs)

    def est_local(self):
        return self.type_fournisseur == 'Local'

    def est_etranger(self):
        return self.type_fournisseur == 'Foreign'
    
    def get_vendor_avg_rating(self):
        """Retourne la moyenne des évaluations vendor (60% du total)"""
        avg = self.evaluations.aggregate(avg=Avg('vendor_final_rating'))['avg']
        return Decimal(str(avg)) if avg else Decimal('0.00')
    
    def get_buyer_avg_rating(self):
        """Retourne la moyenne des évaluations acheteur (40% du total)"""
        avg = self.buyer_evaluations.aggregate(avg=Avg('buyer_final_rating'))['avg']
        return Decimal(str(avg)) if avg else Decimal('0.00')
    
    def get_weighted_rating(self):
        """
        Calcule la note globale pondérée:
        - Évaluation Vendor: 60%
        - Évaluation Acheteur: 40%
        """
        vendor_avg = self.get_vendor_avg_rating()
        buyer_avg = self.get_buyer_avg_rating()
        
        # Si aucune évaluation n'existe, retourner 0
        if vendor_avg == 0 and buyer_avg == 0:
            return Decimal('0.00')
        
        # Calcul pondéré: 60% vendor + 40% buyer
        weighted = (vendor_avg * Decimal('0.60')) + (buyer_avg * Decimal('0.40'))
        return weighted.quantize(Decimal('0.01'))
    
    def get_evaluation_counts(self):
        """Retourne le nombre d'évaluations de chaque type"""
        return {
            'vendor': self.evaluations.count(),
            'buyer': self.buyer_evaluations.count(),
            'total': self.evaluations.count() + self.buyer_evaluations.count()
        }
    
    def get_weighted_rating_badge(self):
        """Retourne un badge de couleur selon la note globale pondérée"""
        rating = float(self.get_weighted_rating())
        if rating >= 8:
            return {'class': 'success', 'label': 'Excellent'}
        elif rating >= 6:
            return {'class': 'primary', 'label': 'Bon'}
        elif rating >= 4:
            return {'class': 'warning', 'label': 'Moyen'}
        else:
            return {'class': 'danger', 'label': 'Faible'}