from django.db import models
from django.conf import settings
from decimal import Decimal


class SupplierEvaluation(models.Model):
    """
    Modèle pour stocker les évaluations des fournisseurs
    """
    CRITERIA_CHOICES = {
        'delivery_compliance': {
            0: 'Non conforme',
            1: 'Non conforme',
            2: 'Conformité : 25% par rapport au besoin exprimé',
            3: 'Conformité : 25% par rapport au besoin exprimé',
            4: 'Conformité : 25% par rapport au besoin exprimé',
            5: 'Conformité : 50% par rapport au besoin exprimé',
            6: 'Conformité : 50% par rapport au besoin exprimé',
            7: 'Conforme au besoin',
            8: 'Conforme au besoin',
            9: 'Conforme au besoin',
            10: 'Supérieure / Meilleur que le besoin exprimé mais au même coût'
        },
        'delivery_timeline': {
            0: 'Aucune livraison effectuée',
            1: 'Aucune livraison effectuée',
            2: 'Retard dans la livraison sans le notifier',
            3: 'Retard dans la livraison sans le notifier',
            4: 'Retard négocié et non respect du nouveau planning avec explication donnée',
            5: 'Retard négocié et non respect du nouveau planning avec explication donnée',
            6: 'Retard négocié et non respect du nouveau planning avec explication donnée',
            7: 'Respect des délais',
            8: 'Respect des délais',
            9: 'Respect des délais',
            10: 'En avance sur le délai de livraison prévue'
        },
        'advising_capability': {
            0: 'Conseil inexistant',
            1: 'Conseil inexistant',
            2: 'Sur demande - Conseil donné mais pas utile',
            3: 'Sur demande - Conseil donné mais pas utile',
            4: 'Sur demande - Conseil donné utile mais incomplet',
            5: 'Sur demande - Conseil donné utile mais incomplet',
            6: 'Sur demande - Conseil donné utile mais incomplet',
            7: 'Capacité à conseiller répond à nos attentes',
            8: 'Capacité à conseiller répond à nos attentes',
            9: 'Capacité à conseiller répond à nos attentes',
            10: 'Transfert de compétence & formation régulière du client'
        },
        'after_sales_qos': {
            0: 'SAV inexistant',
            1: 'SAV inexistant',
            2: 'Pas adapté à nos attentes',
            3: 'Pas adapté à nos attentes',
            4: 'Adapté à 50% à nos attentes sans respecter les délais',
            5: 'Adapté à 50% à nos attentes sans respecter les délais',
            6: 'Adapté à 50% à nos attentes sans respecter les délais',
            7: '100% des requêtes et des plaintes résolues dans les délais',
            8: '100% des requêtes et des plaintes résolues dans les délais',
            9: '100% des requêtes et des plaintes résolues dans les délais',
            10: 'Anticipation des problèmes / Aucun incident n\'est à signaler'
        },
        'vendor_relationship': {
            0: 'Aucun contact',
            1: 'Aucun contact',
            2: 'Injoignable en dehors des visites / événements / pendant l\'exécution d\'une commande',
            3: 'Injoignable en dehors des visites / événements / pendant l\'exécution d\'une commande',
            4: 'Joignable après 2 ou 3 jours de relance, rappels …',
            5: 'Joignable après 2 ou 3 jours de relance, rappels …',
            6: 'Joignable après 2 ou 3 jours de relance, rappels …',
            7: 'Bon contact / Prestataire réactif',
            8: 'Bon contact / Prestataire réactif',
            9: 'Bon contact / Prestataire réactif',
            10: 'Bon contact / Prestataire très réactif'
        }
    }

    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name="Fournisseur"
    )
    
    # Critères d'évaluation (notes de 0 à 10)
    delivery_compliance = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Delivery Compliance to Order (Quantity & Quality)",
        help_text="Note de 0 à 10"
    )
    delivery_timeline = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Delivery Execution Timeline",
        help_text="Note de 0 à 10"
    )
    advising_capability = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Vendor Advising Capability",
        help_text="Note de 0 à 10"
    )
    after_sales_qos = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="After Sales Services QOS",
        help_text="Note de 0 à 10"
    )
    vendor_relationship = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Vendor Relationship",
        help_text="Note de 0 à 10"
    )
    
    # Note finale calculée automatiquement
    vendor_final_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Vendor Final Rating",
        help_text="Moyenne des 5 critères (calculée automatiquement)"
    )
    
    # Commentaires optionnels
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaires"
    )
    
    # Métadonnées
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Évaluateur"
    )
    date_evaluation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'évaluation"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )

    class Meta:
        verbose_name = "Évaluation fournisseur"
        verbose_name_plural = "Évaluations fournisseurs"
        ordering = ['-date_evaluation']

    def __str__(self):
        return f"Évaluation {self.supplier.nom_complet_organisation} - {self.date_evaluation.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        """Calcule automatiquement la moyenne avant la sauvegarde"""
        scores = [
            self.delivery_compliance,
            self.delivery_timeline,
            self.advising_capability,
            self.after_sales_qos,
            self.vendor_relationship
        ]
        self.vendor_final_rating = Decimal(str(sum(scores) / len(scores))) if scores else Decimal('0.00')
        super().save(*args, **kwargs)

    def get_criteria_description(self, criteria_name, score):
        """Retourne la description du critère pour une note donnée"""
        if criteria_name in self.CRITERIA_CHOICES:
            return self.CRITERIA_CHOICES[criteria_name].get(score, f"Score: {score}")
        return f"Score: {score}"

    def get_total_score(self):
        """Calcule le score total sur 50"""
        return (
            self.delivery_compliance +
            self.delivery_timeline +
            self.advising_capability +
            self.after_sales_qos +
            self.vendor_relationship
        )
    
    def get_rating_badge(self):
        """Retourne un badge de couleur selon la note finale"""
        rating = float(self.vendor_final_rating)
        if rating >= 8:
            return {'class': 'success', 'label': 'Excellent'}
        elif rating >= 6:
            return {'class': 'primary', 'label': 'Bon'}
        elif rating >= 4:
            return {'class': 'warning', 'label': 'Moyen'}
        else:
            return {'class': 'danger', 'label': 'Faible'}


class BuyerEvaluation(models.Model):
    """
    Modèle pour stocker les évaluations acheteur des fournisseurs
    Cette évaluation compte pour 40% de la note globale
    """
    CRITERIA_CHOICES = {
        'price_flexibility': {
            0: 'Aucune flexibilité',
            1: 'Aucune flexibilité',
            2: 'Flexibilité très limitée',
            3: 'Flexibilité très limitée',
            4: 'Flexibilité limitée sur certains produits',
            5: 'Flexibilité moyenne',
            6: 'Flexibilité moyenne',
            7: 'Bonne flexibilité',
            8: 'Bonne flexibilité',
            9: 'Très bonne flexibilité',
            10: 'Excellente flexibilité avec négociations avantageuses'
        },
        'rfx_deadline_compliance': {
            0: 'Aucune réponse',
            1: 'Aucune réponse',
            2: 'Retard important sans justification',
            3: 'Retard important sans justification',
            4: 'Retard avec justification',
            5: 'Retard avec justification',
            6: 'Retard mineur',
            7: 'Respect des délais',
            8: 'Respect des délais',
            9: 'Respect des délais',
            10: 'Réponse en avance sur les délais'
        },
        'advisory_capability': {
            0: 'Aucun conseil',
            1: 'Aucun conseil',
            2: 'Conseils inadaptés',
            3: 'Conseils inadaptés',
            4: 'Conseils basiques',
            5: 'Conseils basiques',
            6: 'Conseils utiles mais incomplets',
            7: 'Bons conseils',
            8: 'Bons conseils',
            9: 'Excellents conseils proactifs',
            10: 'Expertise exceptionnelle et innovation'
        },
        'relationship_quality': {
            0: 'Aucun contact',
            1: 'Aucun contact',
            2: 'Interlocuteurs injoignables',
            3: 'Interlocuteurs injoignables',
            4: 'Réactivité faible (> 3 jours)',
            5: 'Réactivité moyenne (2-3 jours)',
            6: 'Réactivité moyenne (2-3 jours)',
            7: 'Bonne réactivité (< 24h)',
            8: 'Bonne réactivité (< 24h)',
            9: 'Excellente réactivité (< 12h)',
            10: 'Réactivité exceptionnelle et proactive'
        },
        'rfx_response_quality': {
            0: 'Aucune réponse',
            1: 'Aucune réponse',
            2: 'Réponses incomplètes',
            3: 'Réponses incomplètes',
            4: 'Réponses partielles',
            5: 'Réponses acceptables',
            6: 'Réponses acceptables',
            7: 'Bonnes réponses complètes',
            8: 'Bonnes réponses complètes',
            9: 'Excellentes réponses détaillées',
            10: 'Réponses exceptionnelles avec valeur ajoutée'
        },
        'credit_policy': {
            0: 'Paiement 100% à la commande',
            1: 'Paiement 100% à la commande',
            2: 'Acompte > 80%',
            3: 'Acompte > 80%',
            4: 'Acompte 60-80%',
            5: 'Acompte 40-60%',
            6: 'Acompte 40-60%',
            7: 'Acompte 20-40%',
            8: 'Acompte < 20%',
            9: 'Acompte < 20%',
            10: 'Aucun acompte requis / Crédit fournisseur'
        }
    }

    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='buyer_evaluations',
        verbose_name="Fournisseur"
    )
    
    # Critères d'évaluation acheteur (notes de 0 à 10)
    price_flexibility = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Flexibilité sur les prix",
        help_text="Note de 0 à 10"
    )
    rfx_deadline_compliance = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Respect des délais (Réponse au RFX)",
        help_text="Note de 0 à 10"
    )
    advisory_capability = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Capacité à conseiller (nouveau produit, dans l'exécution de projet)",
        help_text="Note de 0 à 10"
    )
    relationship_quality = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Contact relationnel (Réactivité des interlocuteurs)",
        help_text="Note de 0 à 10"
    )
    rfx_response_quality = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Qualité des réponses aux RFx (eSourcing, Mail)",
        help_text="Note de 0 à 10"
    )
    credit_policy = models.IntegerField(
        choices=[(i, f"{i}") for i in range(11)],
        verbose_name="Politique de crédit (exigence vis-à-vis des acomptes)",
        help_text="Note de 0 à 10"
    )
    
    # Note finale calculée automatiquement
    buyer_final_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Note finale acheteur",
        help_text="Moyenne des 6 critères (calculée automatiquement)"
    )
    
    # Commentaires optionnels
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaires"
    )
    
    # Métadonnées
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Évaluateur"
    )
    date_evaluation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'évaluation"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )

    class Meta:
        verbose_name = "Évaluation acheteur"
        verbose_name_plural = "Évaluations acheteur"
        ordering = ['-date_evaluation']

    def __str__(self):
        return f"Évaluation Acheteur {self.supplier.nom_complet_organisation} - {self.date_evaluation.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        """Calcule automatiquement la moyenne avant la sauvegarde"""
        scores = [
            self.price_flexibility,
            self.rfx_deadline_compliance,
            self.advisory_capability,
            self.relationship_quality,
            self.rfx_response_quality,
            self.credit_policy
        ]
        self.buyer_final_rating = Decimal(str(sum(scores) / len(scores))) if scores else Decimal('0.00')
        super().save(*args, **kwargs)

    def get_criteria_description(self, criteria_name, score):
        """Retourne la description du critère pour une note donnée"""
        if criteria_name in self.CRITERIA_CHOICES:
            return self.CRITERIA_CHOICES[criteria_name].get(score, f"Score: {score}")
        return f"Score: {score}"

    def get_total_score(self):
        """Calcule le score total sur 60"""
        return (
            self.price_flexibility +
            self.rfx_deadline_compliance +
            self.advisory_capability +
            self.relationship_quality +
            self.rfx_response_quality +
            self.credit_policy
        )
    
    def get_rating_badge(self):
        """Retourne un badge de couleur selon la note finale"""
        rating = float(self.buyer_final_rating)
        if rating >= 8:
            return {'class': 'success', 'label': 'Excellent'}
        elif rating >= 6:
            return {'class': 'primary', 'label': 'Bon'}
        elif rating >= 4:
            return {'class': 'warning', 'label': 'Moyen'}
        else:
            return {'class': 'danger', 'label': 'Faible'}
