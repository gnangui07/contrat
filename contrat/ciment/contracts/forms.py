from django import forms
from .models import Contract


class ContractForm(forms.ModelForm):
    """Formulaire pour créer/modifier un contrat"""
    
    class Meta:
        model = Contract
        fields = [
            'numero', 'objet', 'type',
            'type_contrat', 'type_activite',
            'montant', 'devise',
            'date_signature', 'date_effet', 'date_expiry', 'preavis',
            'duree_contrat', 'type_renouvellement',
            'supplier', 'status'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Numéro du contrat (ex: CONT-2024-001)'
            }),
            'objet': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Objet/Description du contrat'
            }),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'type_contrat': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type de contrat (libre)'
            }),
            'type_activite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Type d'activité (libre)"
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Montant total',
                'step': '0.01'
            }),
            'devise': forms.Select(attrs={'class': 'form-control'}),
            'date_signature': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'date_effet': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'date_expiry': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'preavis': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Préavis en jours (défaut: 90)',
                'min': '0'
            }),
            'duree_contrat': forms.Select(attrs={'class': 'form-control'}),
            'type_renouvellement': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des labels en français
        self.fields['numero'].label = 'Numéro du Contrat'
        self.fields['objet'].label = 'Objet du Contrat'
        self.fields['type'].label = 'Type de Contrat'
        self.fields['type_contrat'].label = 'Type de contrat (optionnel)'
        self.fields['type_activite'].label = "Type d'activité (optionnel)"
        self.fields['montant'].label = 'Montant'
        self.fields['devise'].label = 'Devise'
        self.fields['date_signature'].label = 'Date de Signature'
        self.fields['date_effet'].label = 'Date d\'Effet'
        self.fields['date_expiry'].label = 'Date d\'Expiration'
        self.fields['preavis'].label = 'Préavis (jours)'
        self.fields['duree_contrat'].label = 'Durée du contrat (années)'
        self.fields['type_renouvellement'].label = 'Type de renouvellement'
        self.fields['supplier'].label = 'Fournisseur'
        self.fields['status'].label = 'Statut'
        
        # Rendre le statut optionnel lors de la création (il a une valeur par défaut)
        self.fields['status'].required = False
