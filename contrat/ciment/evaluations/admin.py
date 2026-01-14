from django.contrib import admin
from .models import SupplierEvaluation, BuyerEvaluation


@admin.register(SupplierEvaluation)
class SupplierEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'supplier',
        'vendor_final_rating',
        'delivery_compliance',
        'delivery_timeline',
        'advising_capability',
        'after_sales_qos',
        'vendor_relationship',
        'evaluator',
        'date_evaluation',
    ]
    list_filter = ['date_evaluation', 'supplier']
    search_fields = ['supplier__nom_complet_organisation', 'comments']
    readonly_fields = ['vendor_final_rating', 'date_evaluation', 'date_modification']
    
    fieldsets = (
        ('Fournisseur', {
            'fields': ('supplier',)
        }),
        ('Critères d\'évaluation', {
            'fields': (
                'delivery_compliance',
                'delivery_timeline',
                'advising_capability',
                'after_sales_qos',
                'vendor_relationship',
            )
        }),
        ('Résultat', {
            'fields': ('vendor_final_rating',)
        }),
        ('Commentaires', {
            'fields': ('comments',)
        }),
        ('Métadonnées', {
            'fields': ('evaluator', 'date_evaluation', 'date_modification')
        }),
    )


@admin.register(BuyerEvaluation)
class BuyerEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'supplier',
        'buyer_final_rating',
        'price_flexibility',
        'rfx_deadline_compliance',
        'advisory_capability',
        'relationship_quality',
        'rfx_response_quality',
        'credit_policy',
        'evaluator',
        'date_evaluation',
    ]
    list_filter = ['date_evaluation', 'supplier']
    search_fields = ['supplier__nom_complet_organisation', 'comments']
    readonly_fields = ['buyer_final_rating', 'date_evaluation', 'date_modification']
    
    fieldsets = (
        ('Fournisseur', {
            'fields': ('supplier',)
        }),
        ('Critères d\'évaluation acheteur', {
            'fields': (
                'price_flexibility',
                'rfx_deadline_compliance',
                'advisory_capability',
                'relationship_quality',
                'rfx_response_quality',
                'credit_policy',
            )
        }),
        ('Résultat', {
            'fields': ('buyer_final_rating',)
        }),
        ('Commentaires', {
            'fields': ('comments',)
        }),
        ('Métadonnées', {
            'fields': ('evaluator', 'date_evaluation', 'date_modification')
        }),
    )
