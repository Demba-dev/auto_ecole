from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import admin_required
from .models import Employe, MoniteurProfile, AffectationMoniteur, DisponibiliteMoniteur
from .forms import EmployeForm, MoniteurProfileForm, AffectationMoniteurForm, DisponibiliteMoniteurForm






@admin_required
def personnel_hub(request, section='employe'):
    context = {'active': section}

    if section == 'employe':
        context['employes'] = Employe.objects.all()
    elif section == 'moniteur':
        context['moniteurs'] = MoniteurProfile.objects.all()
    elif section == 'affectation':
        context['affectations'] = AffectationMoniteur.objects.all()
    elif section == 'disponibilite':
        context['disponibilites'] = DisponibiliteMoniteur.objects.all()

    return render(request, 'personnel/hub.html', context)

# -------------------------
# Liste et détails (déjà fait)
# -------------------------
# employe_list, employe_detail, moniteur_list, affectation_list, disponibilite_list
# ... (garder les fonctions précédentes)

@admin_required
def employe_list(request):
    employes = Employe.objects.select_related('user')
    return render(request, 'personnel/employe_list.html', {
        'employes': employes
    })

@admin_required
def employe_detail(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    moniteur_profile = None

    if employe.type_employe == 'MONITEUR':
        moniteur_profile = MoniteurProfile.objects.filter(employe=employe).first()

    return render(request, 'personnel/employe_detail.html', {
        'employe': employe,
        'moniteur_profile': moniteur_profile
    })

@admin_required
def moniteur_list(request):
    moniteurs = MoniteurProfile.objects.select_related('employe', 'employe__user')
    return render(request, 'personnel/moniteur_list.html', {
        'moniteurs': moniteurs
    })


@admin_required
def affectation_list(request):
    affectations = AffectationMoniteur.objects.select_related(
        'apprenant',
        'moniteur',
        'moniteur__user'
    )
    return render(request, 'personnel/affectation_list.html', {
        'affectations': affectations
    })

@admin_required
def disponibilite_list(request):
    disponibilites = DisponibiliteMoniteur.objects.select_related(
        'moniteur',
        'moniteur__user'
    )
    return render(request, 'personnel/disponibilite_list.html', {
        'disponibilites': disponibilites
    })


# -------------------------
# CRUD Employe
# -------------------------
@admin_required
def employe_create(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('personnel:employe_list')
    else:
        form = EmployeForm()
    return render(request, 'personnel/employe_form.html', {'form': form, 'title': 'Ajouter un employé'})


@admin_required
def employe_update(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('personnel:employe_list')
    else:
        form = EmployeForm(instance=employe)
    return render(request, 'personnel/employe_form.html', {'form': form, 'title': 'Modifier un employé'})


@admin_required
def employe_delete(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        employe.delete()
        return redirect('personnel:employe_list')
    return render(request, 'personnel/employe_confirm_delete.html', {'employe': employe})


# -------------------------
# CRUD MoniteurProfile
# -------------------------
@admin_required
def moniteur_create(request):
    if request.method == 'POST':
        form = MoniteurProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('personnel:moniteur_list')
    else:
        form = MoniteurProfileForm()
    return render(request, 'personnel/moniteur_form.html', {'form': form, 'title': 'Ajouter un moniteur'})


@admin_required
def moniteur_update(request, pk):
    moniteur = get_object_or_404(MoniteurProfile, pk=pk)
    if request.method == 'POST':
        form = MoniteurProfileForm(request.POST, instance=moniteur)
        if form.is_valid():
            form.save()
            return redirect('personnel:moniteur_list')
    else:
        form = MoniteurProfileForm(instance=moniteur)
    return render(request, 'personnel/moniteur_form.html', {'form': form, 'title': 'Modifier un moniteur'})


@admin_required
def moniteur_delete(request, pk):
    moniteur = get_object_or_404(MoniteurProfile, pk=pk)
    if request.method == 'POST':
        moniteur.delete()
        return redirect('personnel:moniteur_list')
    return render(request, 'personnel/moniteur_confirm_delete.html', {'moniteur': moniteur})


# -------------------------
# CRUD AffectationMoniteur
# -------------------------
@admin_required
def affectation_create(request):
    if request.method == 'POST':
        form = AffectationMoniteurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('personnel:affectation_list')
    else:
        form = AffectationMoniteurForm()
    return render(request, 'personnel/affectation_form.html', {'form': form, 'title': 'Nouvelle affectation'})


@admin_required
def affectation_update(request, pk):
    affectation = get_object_or_404(AffectationMoniteur, pk=pk)
    if request.method == 'POST':
        form = AffectationMoniteurForm(request.POST, instance=affectation)
        if form.is_valid():
            form.save()
            return redirect('personnel:affectation_list')
    else:
        form = AffectationMoniteurForm(instance=affectation)
    return render(request, 'personnel/affectation_form.html', {'form': form, 'title': 'Modifier affectation'})


@admin_required
def affectation_delete(request, pk):
    affectation = get_object_or_404(AffectationMoniteur, pk=pk)
    if request.method == 'POST':
        affectation.delete()
        return redirect('personnel:affectation_list')
    return render(request, 'personnel/affectation_confirm_delete.html', {'affectation': affectation})


# -------------------------
# CRUD DisponibiliteMoniteur
# -------------------------
@admin_required
def disponibilite_create(request):
    if request.method == 'POST':
        form = DisponibiliteMoniteurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('personnel:disponibilite_list')
    else:
        form = DisponibiliteMoniteurForm()
    return render(request, 'personnel/disponibilite_form.html', {'form': form, 'title': 'Nouvelle disponibilité'})


@admin_required
def disponibilite_update(request, pk):
    dispo = get_object_or_404(DisponibiliteMoniteur, pk=pk)
    if request.method == 'POST':
        form = DisponibiliteMoniteurForm(request.POST, instance=dispo)
        if form.is_valid():
            form.save()
            return redirect('personnel:disponibilite_list')
    else:
        form = DisponibiliteMoniteurForm(instance=dispo)
    return render(request, 'personnel/disponibilite_form.html', {'form': form, 'title': 'Modifier disponibilité'})


@admin_required
def disponibilite_delete(request, pk):
    dispo = get_object_or_404(DisponibiliteMoniteur, pk=pk)
    if request.method == 'POST':
        dispo.delete()
        return redirect('personnel:disponibilite_list')
    return render(request, 'personnel/disponibilite_confirm_delete.html', {'disponibilite': dispo})
