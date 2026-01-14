from django import forms
from .models import SupplierEvaluation, BuyerEvaluation


class SupplierEvaluationForm(forms.ModelForm):
    """Formulaire pour créer une évaluation de fournisseur (Vendor)"""
    
    class Meta:
        model = SupplierEvaluation
        fields = [
            'supplier',
            'delivery_compliance',
            'delivery_timeline',
            'advising_capability',
            'after_sales_qos',
            'vendor_relationship',
            'comments',
        ]
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'delivery_compliance': forms.Select(attrs={'class': 'form-control'}),
            'delivery_timeline': forms.Select(attrs={'class': 'form-control'}),
            'advising_capability': forms.Select(attrs={'class': 'form-control'}),
            'after_sales_qos': forms.Select(attrs={'class': 'form-control'}),
            'vendor_relationship': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Commentaires additionnels (optionnel)'}),
        }


class BuyerEvaluationForm(forms.ModelForm):
    """Formulaire pour créer une évaluation acheteur"""
    
    class Meta:
        model = BuyerEvaluation
        fields = [
            'supplier',
            'price_flexibility',
            'rfx_deadline_compliance',
            'advisory_capability',
            'relationship_quality',
            'rfx_response_quality',
            'credit_policy',
            'comments',
        ]
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'price_flexibility': forms.Select(attrs={'class': 'form-control'}),
            'rfx_deadline_compliance': forms.Select(attrs={'class': 'form-control'}),
            'advisory_capability': forms.Select(attrs={'class': 'form-control'}),
            'relationship_quality': forms.Select(attrs={'class': 'form-control'}),
            'rfx_response_quality': forms.Select(attrs={'class': 'form-control'}),
            'credit_policy': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Commentaires additionnels (optionnel)'}),
        }
