from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Supplier, Banque
from .forms import SupplierForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.mail import send_mail, EmailMultiAlternatives
from evaluations.models import SupplierEvaluation, BuyerEvaluation
from django.template.loader import render_to_string
import json
from django.views.decorators.http import require_GET


@login_required
def autocomplete_banques(request):
    """API d'autocomplétion pour les banques"""
    query = request.GET.get('q', '')
    
    if query:
        banques = Banque.objects.filter(
            Q(nom__icontains=query) |
            Q(sigle__icontains=query) |
            Q(code_banque__icontains=query)
        )[:10]
    else:
        banques = Banque.objects.all()[:10]
    
    results = []
    for banque in banques:
        results.append({
            'id': banque.id,
            'nom': banque.nom,
            'sigle': banque.sigle,
            'code_banque': banque.code_banque,
            'code_bic': banque.code_bic,
            'iban_prefix': banque.iban_prefix,
        })
    
    return JsonResponse({'results': results})


@login_required
def get_banque_details(request, banque_id):
    """Récupérer les détails d'une banque spécifique"""
    try:
        banque = Banque.objects.get(id=banque_id)
        return JsonResponse({
            'success': True,
            'nom': banque.nom,
            'sigle': banque.sigle,
            'code_banque': banque.code_banque,
            'code_bic': banque.code_bic,
            'iban_prefix': banque.iban_prefix,
        })
    except Banque.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Banque non trouvée'})


@login_required
def supplier_list(request):
    """Liste des fournisseurs"""
    suppliers = Supplier.objects.all()
    
    # Filtrage par type (Local/Foreign)
    type_fournisseur = request.GET.get('type')
    if type_fournisseur:
        suppliers = suppliers.filter(type_fournisseur=type_fournisseur)
    
    # Filtrage par catégorie
    categorie = request.GET.get('categorie')
    if categorie:
        suppliers = suppliers.filter(type_categorie=categorie)
    
    # Filtrage par statut actif
    actif = request.GET.get('actif')
    if actif:
        suppliers = suppliers.filter(actif=(actif == '1'))
    
    # Recherche
    search = request.GET.get('search')
    if search:
        suppliers = suppliers.filter(
            Q(nom_complet_organisation__icontains=search) | 
            Q(email__icontains=search) |
            Q(telephone__icontains=search) |
            Q(adresse_physique__icontains=search)
        )
    
    context = {
        'suppliers': suppliers,
    }
    return render(request, 'suppliers/supplier_list.html', context)


@login_required
def supplier_detail(request, pk):
    """Détail d'un fournisseur"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    context = {
        'supplier': supplier,
    }
    return render(request, 'suppliers/supplier_detail.html', context)


@login_required
def supplier_create(request):
    """Créer un fournisseur"""
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Fournisseur "{supplier.nom_complet_organisation}" créé avec succès.')
            return redirect('suppliers:detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    
    context = {'form': form}
    return render(request, 'suppliers/supplier_form.html', context)


@login_required
def supplier_edit(request, pk):
    """Modifier un fournisseur"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Fournisseur "{supplier.nom_complet_organisation}" modifié avec succès.')
            return redirect('suppliers:detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    
    context = {'form': form, 'supplier': supplier}
    return render(request, 'suppliers/supplier_form.html', context)


@login_required
def supplier_delete(request, pk):
    """Supprimer un fournisseur (confirmation gérée côté client via SweetAlert)"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        nom = supplier.nom_complet_organisation
        supplier.delete()
        messages.success(request, f'Fournisseur "{nom}" supprimé avec succès.')
        return redirect('suppliers:list')
    
    # En GET, on ne rend plus de page de confirmation (SweetAlert côté client)
    return redirect('suppliers:list')


def get_criteria_descriptions():
    # Acheteur : tuples (français, anglais)
    acheteur_criteres = [
        ("Flexibilité sur les prix", "Price flexibility"),
        ("Respect des délais (RFx)", "RFx deadline compliance"),
        ("Capacité de conseil", "Advisory capability"),
        ("Qualité relationnelle", "Relationship quality"),
        ("Qualité des réponses (RFx)", "RFx response quality"),
        ("Politique de crédit", "Credit policy")
    ]
    demandeur_criteres = [
        "Livraison conforme à la commande",
        "Délais de livraison",
        "Capacité de conseil",
        "Service après-vente",
        "Disponibilité et relation fournisseur"
    ]
    return acheteur_criteres, demandeur_criteres

# --- nouvelle version GET (mailto) ---
@login_required
@require_GET
def get_eval_summary(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    types = request.GET.get('types', '').split(',')
    body = f"Fournisseur : {supplier.nom_complet_organisation}\nEmail : {supplier.email}\n\n"
    acheteur_criteres, demandeur_criteres = get_criteria_descriptions()

    # Blocage pour demandeur si aucune évaluation
    if 'demandeur' in types:
        vendor_evals = SupplierEvaluation.objects.filter(supplier=supplier).order_by('-id')
        if not vendor_evals.exists():
            return JsonResponse({'text_body': '', 'error': "Impossible d'envoyer ce mail car aucune évaluation demandeur n'a été recensée pour ce fournisseur. Veuillez d'abord l'évaluer dans le module Demandeur."})

    if 'acheteur' in types:
        
        body += 'Bonjour,\n\nMerci de bien vouloir évaluer le fournisseur suivant en renseignant une note (0 à 10) pour chaque critère :\n'
        for fr, en in acheteur_criteres:
            body += f"- {fr} : ____/10\n"
        
        body += 'Dear Sir/Madam,\n\nKindly evaluate the following supplier by assigning a score (0 to 10) for each criterion:\n'
        for fr, en in acheteur_criteres:
            body += f"- {en}: ____/10\n"
        body += '\n'
    if 'demandeur' in types:
        vendor_evals = SupplierEvaluation.objects.filter(supplier=supplier).order_by('-id')
        body += '\n== Résultats de l\'évaluation demandeur ==\n'
        for eval in vendor_evals[:1]:
            body += f"Note finale : {eval.vendor_final_rating}/10\n"
            eval_map = [
                ("Livraison conforme à la commande", eval.delivery_compliance),
                ("Délais de livraison", eval.delivery_timeline),
                ("Capacité de conseil", eval.advising_capability),
                ("Service après-vente", eval.after_sales_qos),
                ("Disponibilité et relation fournisseur", eval.vendor_relationship)
            ]
            for crit, note in eval_map:
                body += f"- {crit} : {note}/10\n"
    body += f'\nNote globale pondérée : {supplier.get_weighted_rating()} / 10\n-- Ceci est un envoi automatique | This is an automatic notification.'
    return JsonResponse({'text_body': body})

# --- version backend SMTP corrigée ---
@login_required
@csrf_exempt
def send_supplier_mail(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest('Méthode non autorisée')

    try:
        data = json.loads(request.body)
        types = data.get('types', [])
        recipients = [e.strip() for e in data.get('dest', '').split(',') if e.strip()]
        supplier = get_object_or_404(Supplier, pk=pk)
    except Exception as ex:
        return JsonResponse({"success": False, "error": "Paramètres invalides."})

    # Blocage serveur SMTP pour demandeur si aucune évaluation
    if 'demandeur' in types:
        vendor_evals = SupplierEvaluation.objects.filter(supplier=supplier).order_by('-id')
        if not vendor_evals.exists():
            return JsonResponse({'success': False, 'error': "Impossible d'envoyer ce mail car aucune évaluation demandeur n'a été recensée pour ce fournisseur. Veuillez d'abord l'évaluer dans le module Demandeur."})

    subject_parts = ["Évaluation fournisseur : {}".format(supplier.nom_complet_organisation)]
    body_parts = [f"<h2>Fournisseur : {supplier.nom_complet_organisation}<br>Email : {supplier.email}</h2>"]
    acheteur_criteres, demandeur_criteres = get_criteria_descriptions()
    if 'acheteur' in types:
        body_parts.append('<hr><h3 style="color:#2980b9;">Version française</h3><p>Merci de bien vouloir évaluer le fournisseur suivant en renseignant une note (0 à 10) pour chaque critère :</p><ul>')
        for fr, en in acheteur_criteres:
            body_parts.append(f'<li>{fr} : ____/10</li>')
        body_parts.append('</ul>')
        body_parts.append('<h3 style="color:#2980b9;">English version</h3><p>Kindly evaluate the following supplier by assigning a score (0 to 10) for each criterion:</p><ul>')
        for fr, en in acheteur_criteres:
            body_parts.append(f'<li>{en}: ____/10</li>')
        body_parts.append('</ul>')
    if 'demandeur' in types:
        vendor_evals = SupplierEvaluation.objects.filter(supplier=supplier).order_by('-id')
        body_parts.append('<h3>Résultats de l\'évaluation Demandeur</h3>')
        if not vendor_evals.exists():
            body_parts.append('<p style="color:#999;">Aucune évaluation demandeur disponible.</p>')
        for eval in vendor_evals[:1]:
            body_parts.append(f'<b>Note finale :</b> {eval.vendor_final_rating}/10<br>')
            eval_map = [
                ("Livraison conforme à la commande", eval.delivery_compliance),
                ("Délais de livraison", eval.delivery_timeline),
                ("Capacité de conseil", eval.advising_capability),
                ("Service après-vente", eval.after_sales_qos),
                ("Disponibilité et relation fournisseur", eval.vendor_relationship)
            ]
            for crit, note in eval_map:
                body_parts.append(f"- {crit} : {note}/10<br>")
    body_parts.append(f'<hr><b>Note globale pondérée :</b> {supplier.get_weighted_rating()} / 10<br>-- Ceci est un envoi automatique | This is an automatic notification')
    subject = ' | '.join(subject_parts)
    html_body = '<br>'.join(body_parts)
    try:
        msg = EmailMultiAlternatives(subject, html_body, request.user.email, recipients)
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return JsonResponse({"success": True})
    except Exception as ex:
        return JsonResponse({"success": False, "error": str(ex)})
