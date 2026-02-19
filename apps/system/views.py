import os
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import admin_required
from django.utils import timezone
from .models import SystemSettings
from .utils import backup_database, get_backups, restore_database

@admin_required
def settings_view(request):
    settings_obj, created = SystemSettings.objects.get_or_create(id=1)
    backups = get_backups()
    
    if request.method == 'POST':
        tab = request.POST.get('tab', 'general')
        
        if tab == 'general':
            settings_obj.app_name = request.POST.get('app_name', settings_obj.app_name)
            settings_obj.address = request.POST.get('address', settings_obj.address)
            settings_obj.phone = request.POST.get('phone', settings_obj.phone)
            settings_obj.email = request.POST.get('email', settings_obj.email)
            if 'app_logo' in request.FILES:
                settings_obj.app_logo = request.FILES['app_logo']
        
        elif tab == 'backup':
            settings_obj.auto_backup = 'auto_backup' in request.POST
            settings_obj.backup_frequency = request.POST.get('backup_frequency', settings_obj.backup_frequency)
            settings_obj.backup_time = request.POST.get('backup_time', settings_obj.backup_time)
            
        settings_obj.save()
        messages.success(request, "Paramètres mis à jour avec succès.")
        return redirect(f"{reverse('system:settings')}?tab={tab}")
        
    return render(request, 'system/settings.html', {
        'settings': settings_obj,
        'backups': backups
    })

@admin_required
def create_backup(request):
    try:
        backup_path = backup_database()
        settings_obj = SystemSettings.objects.get(id=1)
        settings_obj.last_backup = timezone.now()
        settings_obj.save()
        messages.success(request, f"Sauvegarde créée avec succès : {os.path.basename(backup_path)}")
    except Exception as e:
        messages.error(request, f"Erreur lors de la création de la sauvegarde : {str(e)}")
        
    return redirect(f"{reverse('system:settings')}?tab=backup")

@admin_required
def restore_backup(request, filename):
    try:
        if restore_database(filename):
            messages.success(request, "La base de données a été restaurée avec succès.")
        else:
            messages.error(request, "Fichier de sauvegarde introuvable.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la restauration : {str(e)}")
        
    return redirect(f"{reverse('system:settings')}?tab=backup")
