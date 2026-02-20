from django.shortcuts import render, get_object_or_404, redirect
from apps.accounts.decorators import admin_required
from .models import Vehicule, Maintenance
from .forms import VehiculeForm, MaintenanceForm

from django.db.models import Sum
from django.utils import timezone

# ==========================
# CRUD Vehicule
# ==========================


def is_admin_or_staff(user):
    return user.is_superuser or user.is_staff



@admin_required
def vehicules_hub(request, section=None):
    """
    Hub Véhicules : affiche le hub ou les listes selon la section
    """
    context = {'active': section or 'hub'}
    
    if section == 'vehicules':
        context['vehicules'] = Vehicule.objects.all()
        template_name = 'vehicules/vehicule_list.html'
    elif section == 'maintenances':
        maintenances = Maintenance.objects.select_related('vehicule').all().order_by('-date')
        context['maintenances'] = maintenances
        context['total_interventions'] = maintenances.count()
        context['total_depenses'] = maintenances.aggregate(total=Sum('montant'))['total'] or 0
        context['echeances_a_venir'] = maintenances.filter(prochaine_echeance__gte=timezone.now().date()).count()
        context['today'] = timezone.now().date()
        template_name = 'vehicules/maintenance_list.html'
    else:
        # Statistiques pour le Hub
        vehicules = Vehicule.objects.all()
        maintenances = Maintenance.objects.all()
        
        context['total_vehicules'] = vehicules.count()
        context['disponibles'] = vehicules.filter(statut='DISPONIBLE').count()
        context['en_maintenance'] = vehicules.filter(statut='MAINTENANCE').count()
        context['occupes'] = vehicules.filter(statut='OCCUPE').count()
        context['indisponibles'] = vehicules.filter(statut='INDISPONIBLE').count()
        
        context['maintenances_recentes'] = Maintenance.objects.select_related('vehicule').order_by('-date')[:5]
        context['maintenances_a_venir'] = Maintenance.objects.filter(prochaine_echeance__gte=timezone.now().date()).order_by('prochaine_echeance')[:3]
        context['derniers_vehicules'] = vehicules.order_by('-id')[:5]
        
        template_name = 'vehicules/hub.html'
    
    return render(request, template_name, context)


@admin_required
def vehicule_list(request):
    vehicules = Vehicule.objects.all()
    return render(request, 'vehicules/vehicule_list.html', {'vehicules': vehicules})

@admin_required
def vehicule_create(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicules:vehicule_list')
    else:
        form = VehiculeForm()
    return render(request, 'vehicules/vehicule_form.html', {'form': form})

@admin_required
def vehicule_update(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        form = VehiculeForm(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            return redirect('vehicules:vehicule_list')
    else:
        form = VehiculeForm(instance=vehicule)
    return render(request, 'vehicules/vehicule_form.html', {'form': form})

@admin_required
def vehicule_delete(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        vehicule.delete()
        return redirect('vehicules:vehicule_list')
    return render(request, 'vehicules/vehicule_confirm_delete.html', {'vehicule': vehicule})


# ==========================
# CRUD Maintenance
# ==========================

@admin_required
def maintenance_list(request):
    maintenances = Maintenance.objects.select_related('vehicule').all().order_by('-date')
    total_interventions = maintenances.count()
    total_depenses = maintenances.aggregate(total=Sum('montant'))['total'] or 0
    echeances_a_venir = maintenances.filter(prochaine_echeance__gte=timezone.now().date()).count()
    today = timezone.now().date()
    
    context = {
        'maintenances': maintenances,
        'total_interventions': total_interventions,
        'total_depenses': total_depenses,
        'echeances_a_venir': echeances_a_venir,
        'today': today,
        'active': 'maintenances'
    }
    return render(request, 'vehicules/maintenance_list.html', context)


@admin_required
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicules:maintenance_list')
    else:
        form = MaintenanceForm()
    return render(request, 'vehicules/maintenance_form.html', {'form': form})

@admin_required
def maintenance_update(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        if form.is_valid():
            form.save()
            return redirect('vehicules:maintenance_list')
    else:
        form = MaintenanceForm(instance=maintenance)
    return render(request, 'vehicules/maintenance_form.html', {'form': form})

@admin_required
def maintenance_delete(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    if request.method == 'POST':
        maintenance.delete()
        return redirect('vehicules:maintenance_list')
    return render(request, 'vehicules/maintenance_confirm_delete.html', {'maintenance': maintenance})
