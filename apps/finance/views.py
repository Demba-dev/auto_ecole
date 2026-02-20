from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .forms import TarifForm, ContratForm, PaiementForm
from .models import Tarif, Contrat, Paiement
from apps.apprenants.models import Apprenant, TypePermis
from apps.audit.utils import log_action


def finance_hub(request, section='tarif'):
    context = {'active': section}

    if section == 'tarif':
        context['tarifs'] = Tarif.objects.all()
        context['type_permis_list'] = TypePermis.objects.all()

    elif section == 'contrat':
        contrats = Contrat.objects.all()
        context['contrats'] = contrats
        
        # Statistiques Contrats
        context['montant_total_contrats'] = contrats.aggregate(total=Sum('montant_total'))['total'] or 0
        
        # Comme montant_restant est une property, on calcule les comptes et le solde en Python
        payes = 0
        encours = 0
        solde_total = 0
        for c in contrats:
            restant = c.montant_restant
            solde_total += restant
            if restant == 0:
                payes += 1
            else:
                encours += 1
        
        context['contrats_payes'] = payes
        context['contrats_encours'] = encours
        context['solde_total'] = solde_total

    elif section == 'paiement':
        paiements = Paiement.objects.all()
        context['paiements'] = paiements
        
        # Statistiques Paiements
        now = timezone.now()
        context['total_encaisse'] = paiements.filter(
            date_paiement__month=now.month, 
            date_paiement__year=now.year
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        context['total_paiements'] = paiements.aggregate(total=Sum('montant'))['total'] or 0
        avg = paiements.aggregate(avg=Avg('montant'))['avg'] or 0
        context['moyenne_paiement'] = int(avg)
        
        # Mode de paiement le plus utilisé
        mode_counts = paiements.values('mode').annotate(count=Count('mode')).order_by('-count')
        if mode_counts:
            # On récupère le label du mode
            mode_code = mode_counts[0]['mode']
            # On cherche le label dans les choix du modèle
            mode_label = dict(Paiement.MODE_CHOICES).get(mode_code, mode_code)
            context['mode_plus_utilise'] = mode_label
        else:
            context['mode_plus_utilise'] = "Aucun"

    return render(request, 'finance/hub.html', context)



# ==================Tarif==================
def tarif_create(request):
    form = TarifForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('finance:hub_section', section='tarif')

    return render(request, 'finance/tarif_form.html', {'form': form} )


def tarif_update(request, pk):
    tarif = get_object_or_404(Tarif, pk=pk)
    form = TarifForm(request.POST or None, instance=tarif)

    if form.is_valid():
        form.save()
        return redirect('finance:hub_section', section='tarif')

    return render(request, 'finance/tarif_form.html', {'form': form} )


def tarif_delete(request, pk):
    tarif = get_object_or_404(Tarif, pk=pk)

    if request.method == 'POST':
        tarif.delete()
        return redirect('finance:hub_section', section='tarif')

    return render(request, 'finance/tarif_confirm_delete.html', {'tarif': tarif} )

# =================Contrat==================
def contrat_create(request):
    form = ContratForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('finance:hub_section', section='contrat')

    return render(request, 'finance/contrat_form.html', {'form': form} )


def contrat_update(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)
    form = ContratForm(request.POST or None, instance=contrat)

    if form.is_valid():
        form.save()
        return redirect('finance:hub_section', section='contrat')
    
    return render(request, 'finance/contrat_form.html', {'form': form} )


def contrat_delete(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)

    if request.method == 'POST':
        contrat.delete()
        return redirect('finance:hub_section', section='contrat')

    return render(request, 'finance/contrat_confirm_delete.html', {'contrat': contrat} )

# =================Paiement==================

def paiement_create(request):
    form = PaiementForm(request.POST or None)

    if form.is_valid():
        paiement = form.save()
        log_action(
            user=request.user,
            action='CREATE',
            instance=paiement,
            changes={'montant': str(paiement.montant), 'contrat': str(paiement.contrat)},
            request=request
        )
        return redirect('finance:hub_section', section='paiement')

    return render(request, 'finance/paiement_form.html', {'form': form} )

def paiement_delete(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)

    if request.method == 'POST':
        log_action(
            user=request.user,
            action='DELETE',
            instance=paiement,
            request=request
        )
        paiement.delete()
        return redirect('finance:hub_section', section='paiement')

    return render(request, 'finance/paiement_confirm_delete.html', {'paiement': paiement} )


def paiement_detail(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    return render(request, 'finance/paiement_detail.html', {'paiement': paiement})


def get_contrat_info(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)
    data = {
        'montant_total': float(contrat.montant_total),
        'montant_paye': float(contrat.paiements.aggregate(total=Sum('montant'))['total'] or 0),
        'montant_restant': float(contrat.montant_restant),
    }
    return JsonResponse(data)
