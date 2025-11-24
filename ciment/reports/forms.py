from django import forms


class ExportFilterForm(forms.Form):
    """Formulaire pour filtrer les exports"""
    
    EXPORT_TYPES = [
        ('contracts', 'Contrats'),
        ('suppliers', 'Fournisseurs'),
        ('evaluations', 'Évaluations'),
    ]
    
    export_type = forms.ChoiceField(
        choices=EXPORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Type d\'export'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='À partir du'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Jusqu\'au'
    )
