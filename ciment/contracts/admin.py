from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['numero', 'objet', 'type', 'montant', 'devise', 'status', 'date_expiry']
    list_filter = ['type', 'status', 'date_creation']
    search_fields = ['numero', 'objet', 'supplier__nom']
    readonly_fields = ['date_creation', 'date_modification', 'created_by']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('numero', 'objet', 'type', 'montant', 'devise')
        }),
        ('Dates', {
            'fields': ('date_signature', 'date_effet', 'date_expiry', 'preavis')
        }),
        ('Fournisseur', {
            'fields': ('supplier',)
        }),
        ('Statut', {
            'fields': ('status', 'created_by', 'validated_by')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
