from django import forms
from .models import Supplier, Banque


class SupplierForm(forms.ModelForm):
    """Formulaire pour créer/modifier un fournisseur"""
    
    banque_search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control banque-search',
            'placeholder': 'Rechercher une banque...',
            'autocomplete': 'off'
        }),
        label="Rechercher une banque"
    )
    
    class Meta:
        model = Supplier
        fields = [
            # Informations générales
            'nom_complet_organisation', 'type_fournisseur', 'type_organisation',
            'date_enregistrement', 'adresse_physique', 'adresse_siege_social',
            'telephone', 'email', 'site_web',
            # Représentant légal
            'nom_representant_legal', 'fonction_representant',
            # Personne de contact
            'personne_contact', 'telephone_contact', 'email_contact',
            # Documents légaux
            'registre_commerce', 'numero_compte_contribuable', 'attestation_regularite_fiscale', 'numero_cnps',
            # Informations financières
            'banque_reference', 'banque', 'agence', 'iban', 'bic_swift', 'modalite_paiement',
            # Branche d'activité
            'type_categorie', 'categorie', 'description_categorie',
            # Métadonnées simples
            'actif',
        ]
        widgets = {
            'nom_complet_organisation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom complet de l'organisation"}),
            'type_fournisseur': forms.Select(attrs={'class': 'form-control', 'id': 'id_type_fournisseur'}),
            'type_organisation': forms.Select(attrs={'class': 'form-control'}),
            'date_enregistrement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'adresse_physique': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'adresse_siege_social': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'site_web': forms.URLInput(attrs={'class': 'form-control'}),
            'nom_representant_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'fonction_representant': forms.TextInput(attrs={'class': 'form-control'}),
            'personne_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-control'}),
            'registre_commerce': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_compte_contribuable': forms.TextInput(attrs={'class': 'form-control'}),
            'attestation_regularite_fiscale': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cnps': forms.TextInput(attrs={'class': 'form-control'}),
            'banque_reference': forms.Select(attrs={'class': 'form-control', 'id': 'id_banque_reference'}),
            'banque': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_banque', 'readonly': 'readonly'}),
            'agence': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_iban', 'placeholder': 'CI93...'}),
            'bic_swift': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_bic_swift'}),
            'modalite_paiement': forms.Select(attrs={'class': 'form-control'}),
            'type_categorie': forms.Select(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'description_categorie': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
