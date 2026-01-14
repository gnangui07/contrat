from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        'nom_complet_organisation', 'type_fournisseur', 'type_organisation',
        'categorie', 'type_categorie', 'modalite_paiement', 'actif', 'date_creation'
    ]
    list_filter = ['type_fournisseur', 'type_organisation', 'categorie', 'type_categorie', 'modalite_paiement', 'actif', 'date_creation']
    search_fields = ['nom_complet_organisation', 'email', 'telephone', 'adresse_physique']
    readonly_fields = ['date_creation', 'date_modification']

    fieldsets = (
        ('Informations Générales', {
            'fields': (
                'nom_complet_organisation', 'type_fournisseur', 'type_organisation',
                'date_enregistrement', 'adresse_physique', 'adresse_siege_social',
                'telephone', 'email', 'site_web'
            )
        }),
        ('Représentant Légal', {
            'fields': ('nom_representant_legal', 'fonction_representant')
        }),
        ('Personne de contact', {
            'fields': ('personne_contact', 'telephone_contact', 'email_contact')
        }),
        ('Documents légaux', {
            'fields': ('registre_commerce', 'numero_compte_contribuable', 'attestation_regularite_fiscale', 'numero_cnps')
        }),
        ("Informations financières", {
            'fields': ('banque', 'agence', 'iban', 'bic_swift', 'modalite_paiement')
        }),
        ("Branche d'activité", {
            'fields': ('type_categorie', 'categorie', 'description_categorie')
        }),
        ('Métadonnées', {
            'fields': ('actif', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
