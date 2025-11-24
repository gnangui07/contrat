from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Contract
from .forms import ContractForm


@login_required
def contract_list(request):
    """Liste des contrats"""
    contracts = Contract.objects.all()
    
    # Filtrage par statut
    status = request.GET.get('status')
    if status:
        contracts = contracts.filter(status=status)
    
    # Filtrage par type
    contract_type = request.GET.get('type')
    if contract_type:
        contracts = contracts.filter(type_contrat=contract_type)
    
    # Recherche
    search = request.GET.get('search')
    if search:
        contracts = contracts.filter(
            Q(numero__icontains=search) |
            Q(objet__icontains=search) |
            Q(fournisseur__nom_complet_organisation__icontains=search)
        )
    
    context = {
        'contracts': contracts,
    }
    return render(request, 'contracts/contract_list.html', context)


@login_required
def contract_detail(request, pk):
    """Détail d'un contrat"""
    contract = get_object_or_404(Contract, pk=pk)
    context = {'contract': contract}
    return render(request, 'contracts/contract_detail.html', context)


@login_required
def contract_create(request):
    """Créer un contrat"""
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.save()
            messages.success(request, f"Contrat {contract.numero} créé avec succès !")
            return redirect('contracts:detail', pk=contract.pk)
        else:
            # Afficher les erreurs de validation
            messages.error(request, "Erreur lors de la création du contrat. Veuillez vérifier les champs.")
    else:
        form = ContractForm()
    
    context = {'form': form}
    return render(request, 'contracts/contract_form.html', context)


@login_required
def contract_edit(request, pk):
    """Modifier un contrat"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            contract = form.save()
            messages.success(request, f"Contrat {contract.numero} modifié avec succès !")
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ContractForm(instance=contract)
    
    context = {'form': form, 'contract': contract}
    return render(request, 'contracts/contract_form.html', context)


@login_required
def contract_validate(request, pk):
    """Valider un contrat"""
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les permissions.")
        return redirect('contracts:list')
    
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        contract.status = 'active'
        contract.validated_by = request.user
        contract.save()
        messages.success(request, f"Contrat {contract.numero} validé !")
        return redirect('contracts:detail', pk=contract.pk)
    
    context = {'contract': contract}
    return render(request, 'contracts/contract_detail.html', context)


@login_required
def contract_reject(request, pk):
    """Rejeter un contrat"""
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les permissions.")
        return redirect('contracts:list')
    
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        contract.status = 'rejected'
        contract.validated_by = request.user
        contract.save()
        messages.success(request, f"Contrat {contract.numero} rejeté.")
        return redirect('contracts:detail', pk=contract.pk)
    
    context = {'contract': contract}
    return render(request, 'contracts/contract_detail.html', context)
