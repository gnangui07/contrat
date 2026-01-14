from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from contracts.models import Contract
from suppliers.models import Supplier
from evaluations.models import SupplierEvaluation, BuyerEvaluation
from django.db.models import Q


@login_required
def dashboard(request):
    """Tableau de bord unifié - Adapté selon le rôle de l'utilisateur"""
    
    if request.user.is_superuser:
        # Vue Superuser - Statistiques globales
        total_contracts = Contract.objects.count()
        pending_contracts = Contract.objects.filter(status='pending').count()
        active_contracts = Contract.objects.filter(status='active').count()
        expired_contracts = Contract.objects.filter(status='expired').count()
        
        total_suppliers = Supplier.objects.count()
        # statut_conformite field removed from Supplier model
        compliant_suppliers = Supplier.objects.filter(actif=True).count()
        non_compliant_suppliers = Supplier.objects.filter(actif=False).count()
        
        avg_score = SupplierEvaluation.objects.aggregate(
            avg=Avg('vendor_final_rating')
        )['avg'] or 0

        # KPI fournisseurs / évaluations
        suppliers_count = Supplier.objects.count()
        vendor_evaluations_count = SupplierEvaluation.objects.count()
        buyer_evaluations_count = BuyerEvaluation.objects.count()
        evaluated_suppliers_count = Supplier.objects.filter(
            Q(evaluations__isnull=False) | Q(buyer_evaluations__isnull=False)
        ).distinct().count()
        
        # Alerts module removed for now
        active_alerts = 0
        pending_for_validation = Contract.objects.filter(status='pending').order_by('-date_creation')[:5]
        critical_alerts = []
        
        context = {
            'is_superuser': True,
            'total_contracts': total_contracts,
            'pending_contracts': pending_contracts,
            'active_contracts': active_contracts,
            'expired_contracts': expired_contracts,
            'total_suppliers': total_suppliers,
            'compliant_suppliers': compliant_suppliers,
            'non_compliant_suppliers': non_compliant_suppliers,
            'avg_score': round(avg_score, 2),
            'active_alerts': active_alerts,
            'pending_for_validation': pending_for_validation,
            'critical_alerts': critical_alerts,
            'suppliers_count': suppliers_count,
            'vendor_evaluations_count': vendor_evaluations_count,
            'buyer_evaluations_count': buyer_evaluations_count,
            'evaluated_suppliers_count': evaluated_suppliers_count,
        }
    else:
        # Vue Collaborateur - Données personnelles
        my_contracts = Contract.objects.filter(created_by=request.user)
        my_contracts_count = my_contracts.count()
        my_pending_contracts = my_contracts.filter(status='pending').count()
        my_active_contracts = my_contracts.filter(status='active').count()
        
        # Supplier model doesn't have created_by field
        my_suppliers = Supplier.objects.all()
        my_suppliers_count = my_suppliers.count()
        
        # Alerts module removed for now
        my_alerts = 0
        
        my_evaluations = SupplierEvaluation.objects.filter(evaluator=request.user)
        my_evaluations_count = my_evaluations.count()
        
        context = {
            'is_superuser': False,
            'my_contracts_count': my_contracts_count,
            'my_pending_contracts': my_pending_contracts,
            'my_active_contracts': my_active_contracts,
            'my_suppliers_count': my_suppliers_count,
            'my_alerts': my_alerts,
            'my_evaluations': my_evaluations_count,
            'my_contracts': my_contracts[:5],
            'my_suppliers': my_suppliers[:5],
        }
    
    return render(request, 'dashboard/dashboard_index.html', context)
