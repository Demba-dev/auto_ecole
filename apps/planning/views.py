from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.decorators import admin_required
from django.contrib import messages
from .models import Seance
from django.utils import timezone
from django.db.models import Count

from django.core.exceptions import ValidationError
from .forms import SeanceForm
from apps.system.notifications import notify_apprenant_seance


@admin_required
def planning_hub(request, section=None):
    context = {'active_section': section or 'hub'}
    today = timezone.now().date()

    if section == 'seances':
        context['seances'] = Seance.objects.select_related(
            'apprenant', 'moniteur', 'vehicule'
        ).order_by('-date', '-heure_debut')
        template_name = 'planning/seance_list.html'

    else:
        # Statistiques pour le Hub
        context.update({
            'total_today': Seance.objects.filter(date=today).count(),
            'total_prevu': Seance.objects.filter(statut='PREVU').count(),
            'upcoming_seances': Seance.objects.filter(
                date__gte=today, statut='PREVU'
            ).select_related('apprenant', 'moniteur').order_by('date', 'heure_debut')[:5],
            
            # Distribution par type pour graphique ou badges
            'stats_types': Seance.objects.values('type_seance').annotate(total=Count('id')),
            'stats_statut': Seance.objects.values('statut').annotate(total=Count('id')),
        })
        template_name = 'planning/hub.html'

    return render(request, template_name, context)


@admin_required
def seance_create(request):
    form = SeanceForm(request.POST or None)

    if form.is_valid():
        try:
            seance = form.save()
            # Envoi de l'email de notification (affiché en console car en local)
            notify_apprenant_seance(seance)
            messages.success(request, "Séance créée avec succès.")
            return redirect('planning:planning_hub_section', section='seances')
        except (ValueError, ValidationError) as e:
            form.add_error(None, str(e))

    return render(request, 'planning/seance_form.html', {'form': form})

@admin_required
def seance_update(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    form = SeanceForm(request.POST or None, instance=seance)

    if form.is_valid():
        try:
            form.save()
            messages.success(request, "Séance modifiée avec succès.")
            return redirect('planning:planning_hub_section', section='seances')
        except (ValueError, ValidationError) as e:
            form.add_error(None, str(e))

    return render(request, 'planning/seance_form.html', {'form': form})

@admin_required
def seance_delete(request, pk):
    seance = get_object_or_404(Seance, pk=pk)

    if request.method == "POST":
        seance.delete()
        messages.success(request, "Séance supprimée.")
        return redirect('planning:planning_hub_section', section='seances')

    return render(request, 'planning/seance_confirm_delete.html', {'seance': seance})
