from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import csv
from contracts.models import Contract
from suppliers.models import Supplier
from evaluations.models import SupplierEvaluation


@login_required
@require_http_methods(["GET"])
def export_contracts_csv(request):
    """Exporter les contrats en CSV"""
    if not request.user.is_superuser:
        return HttpResponse("Accès refusé", status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contrats.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Numéro', 'Objet', 'Type', 'Montant', 'Devise', 'Fournisseur', 'Statut', 'Date Échéance'])
    
    for contract in Contract.objects.all():
        writer.writerow([
            getattr(contract, 'numero', ''),
            getattr(contract, 'objet', ''),
            getattr(contract, 'type', ''),
            getattr(contract, 'montant', ''),
            getattr(contract, 'devise', ''),
            getattr(getattr(contract, 'supplier', None), 'nom_complet_organisation', ''),
            getattr(contract, 'status', ''),
            getattr(contract, 'date_expiry', ''),
        ])
    
    return response


@login_required
@require_http_methods(["GET"])
def export_suppliers_csv(request):
    """Exporter les fournisseurs en CSV"""
    if not request.user.is_superuser:
        return HttpResponse("Accès refusé", status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fournisseurs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Catégorie', 'Type fournisseur', 'Email', 'Téléphone', 'Actif'])
    
    for supplier in Supplier.objects.all():
        writer.writerow([
            getattr(supplier, 'nom_complet_organisation', ''),
            getattr(supplier, 'type_categorie', ''),
            getattr(supplier, 'type_fournisseur', ''),
            getattr(supplier, 'email', ''),
            getattr(supplier, 'telephone', ''),
            'Oui' if getattr(supplier, 'actif', False) else 'Non',
        ])
    
    return response


@login_required
@require_http_methods(["GET"])
def export_evaluations_csv(request):
    """Exporter les évaluations en CSV"""
    if not request.user.is_superuser:
        return HttpResponse("Accès refusé", status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="evaluations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Fournisseur',
        'Delivery Compliance',
        'Delivery Timeline',
        'Advising Capability',
        'After Sales QOS',
        'Vendor Relationship',
        'Final Rating',
        'Évaluateur',
        'Date'
    ])
    
    for evaluation in SupplierEvaluation.objects.select_related('supplier', 'evaluator').all():
        writer.writerow([
            getattr(getattr(evaluation, 'supplier', None), 'nom_complet_organisation', ''),
            evaluation.delivery_compliance,
            evaluation.delivery_timeline,
            evaluation.advising_capability,
            evaluation.after_sales_qos,
            evaluation.vendor_relationship,
            evaluation.vendor_final_rating,
            getattr(getattr(evaluation, 'evaluator', None), 'email', ''),
            getattr(evaluation, 'date_evaluation', ''),
        ])
    
    return response


@login_required
def reports_list(request):
    """Liste des rapports disponibles"""
    context = {
        'reports': [
            {'name': 'Contrats', 'url': 'export_contracts_csv', 'icon': 'file-contract'},
            {'name': 'Fournisseurs', 'url': 'export_suppliers_csv', 'icon': 'building'},
            {'name': 'Évaluations', 'url': 'export_evaluations_csv', 'icon': 'chart-bar'},
        ]
    }
    return render(request, 'reports/list.html', context)
