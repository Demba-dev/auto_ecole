import csv
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Apprenant, TypePermis, DossierApprenant, ProgressionConduite
from apps.planning.models import Seance
from datetime import date
from .forms import ApprenantForm, DossierForm, ProgressionForm
from apps.planning.forms import SeanceForm
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import admin_required

@admin_required
def liste_apprenants(request):
    # Base Queryset
    apprenants_all = Apprenant.objects.all()
    
    # Statistiques Globales
    total_count = apprenants_all.count()
    en_formation_count = apprenants_all.filter(statut='formation').count()
    permis_obtenu_count = apprenants_all.filter(statut='permis_obtenu').count()
    taux_reussite = 0
    if total_count > 0:
        taux_reussite = (permis_obtenu_count / total_count) * 100

    # Filtrage
    queryset = apprenants_all.order_by('-date_inscription')
    
    search_query = request.GET.get('q')
    if search_query:
        queryset = queryset.filter(
            Q(nom__icontains=search_query) | 
            Q(prenom__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
        
    statut_filter = request.GET.get('statut')
    if statut_filter:
        queryset = queryset.filter(statut=statut_filter)
        
    permis_filter = request.GET.get('permis')
    if permis_filter:
        queryset = queryset.filter(types_permis__code=permis_filter)

    # Tri
    sort = request.GET.get('sort', 'date_inscription')
    order = request.GET.get('order', 'desc')
    if sort in ['nom', 'prenom', 'date_inscription', 'statut']:
        prefix = '-' if order == 'desc' else ''
        queryset = queryset.order_by(f'{prefix}{sort}')

    # Pagination
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    is_paginated = paginator.num_pages > 1

    types_permis = TypePermis.objects.all()

    context = {
        'apprenants': page_obj,
        'page_obj': page_obj,
        'is_paginated': is_paginated,
        'types_permis': types_permis,
        'apprenants_count': total_count,
        'en_formation_count': en_formation_count,
        'permis_obtenu_count': permis_obtenu_count,
        'taux_reussite': round(taux_reussite, 1)
    }
    return render(request, 'apprenants/liste.html', context)

@admin_required
def detail_apprenant(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    return render(request, 'apprenants/detail.html', {'apprenant': apprenant})

@admin_required
def ajouter_apprenant(request):
    if request.method == 'POST':
        form = ApprenantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_apprenants')
    else:
        form = ApprenantForm()
    return render(request, 'apprenants/form.html', {'form': form})

@admin_required
def modifier_apprenant(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    if request.method == 'POST':
        form = ApprenantForm(request.POST, request.FILES, instance=apprenant)
        if form.is_valid():
            form.save()
            return redirect('liste_apprenants')
    else:
        form = ApprenantForm(instance=apprenant)
    return render(request, 'apprenants/form.html', {'form': form})

@admin_required
def supprimer_apprenant(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    if request.method == 'POST':
        apprenant.delete()
        return redirect('liste_apprenants')
    return render(request, 'apprenants/confirmer_suppression.html', {'apprenant': apprenant})

@admin_required
def planning_apprenant(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    seances = Seance.objects.filter(apprenant=apprenant).order_by('date', 'heure_debut')
    return render(request, 'apprenants/planning.html', {
        'apprenant': apprenant,
        'seances': seances
    })

@admin_required
def exporter_apprenants(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="apprenants.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone', 'Date Inscription'])

    apprenants = Apprenant.objects.all()
    for apprenant in apprenants:
        writer.writerow([
            apprenant.nom,
            apprenant.prenom,
            apprenant.email,
            apprenant.telephone,
            apprenant.date_inscription.strftime('%d/%m/%Y %H:%M')
        ])

    return response

@admin_required
def creer_dossier(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    if request.method == 'POST':
        form = DossierForm(request.POST, request.FILES)
        if form.is_valid():
            dossier = form.save(commit=False)
            dossier.apprenant = apprenant
            dossier.save()
            return redirect('detail_apprenant', pk=pk)
    else:
        form = DossierForm()
    return render(request, 'apprenants/dossier_form.html', {'form': form, 'apprenant': apprenant})

@admin_required
def modifier_dossier(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    dossier = get_object_or_404(DossierApprenant, apprenant=apprenant)
    if request.method == 'POST':
        form = DossierForm(request.POST, request.FILES, instance=dossier)
        if form.is_valid():
            form.save()
            return redirect('detail_apprenant', pk=pk)
    else:
        form = DossierForm(instance=dossier)
    return render(request, 'apprenants/dossier_form.html', {'form': form, 'apprenant': apprenant})

@admin_required
def ajouter_progression(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    # On essaie de récupérer l'existante ou on en crée une nouvelle
    progression, created = ProgressionConduite.objects.get_or_create(apprenant=apprenant)
    
    if request.method == 'POST':
        form = ProgressionForm(request.POST, instance=progression)
        if form.is_valid():
            form.save()
            return redirect('detail_apprenant', pk=pk)
    else:
        form = ProgressionForm(instance=progression)
    return render(request, 'apprenants/progression_form.html', {'form': form, 'apprenant': apprenant})

@admin_required
def planning_apprenant(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    seances = Seance.objects.filter(apprenant=apprenant).order_by('date', 'heure_debut')
    today = date.today()
    
    context = {
        'apprenant': apprenant,
        'seances': seances,
        'today': today,
    }
    return render(request, 'apprenants/planning.html', context)

@admin_required
def creer_seance_apprenant(request, pk):
    apprenant = get_object_or_404(Apprenant, pk=pk)
    if request.method == 'POST':
        form = SeanceForm(request.POST)
        if form.is_valid():
            seance = form.save(commit=False)
            seance.apprenant = apprenant
            seance.save()
            return redirect('planning_apprenant', pk=pk)
    else:
        form = SeanceForm(initial={'apprenant': apprenant})
    
    return render(request, 'apprenants/seance_apprenant_form.html', {
        'form': form,
        'apprenant': apprenant
    })
