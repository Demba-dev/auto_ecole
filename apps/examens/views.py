from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
import csv
from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count
from apps.apprenants.models import Apprenant
from django.urls import reverse
from django.contrib import messages
from apps.accounts.decorators import admin_required
from .models import Examen, EXAM_TYPE_CHOICES, RESULT_CHOICES
from .forms import ExamenForm, ExamenResultForm

# Hub général (optionnel)
@admin_required
def examens_hub(request):
    today = timezone.now().date()
    week_later = today + timedelta(days=7)
    
    # Statistiques générales
    total_examens = Examen.objects.count()
    examens_aujourdhui = Examen.objects.filter(date=today).count()
    examens_en_attente = Examen.objects.filter(result='EN_ATTENTE').count()
    examens_non_payes = Examen.objects.filter(est_paye=False).count()
    examens_avec_resultats = Examen.objects.exclude(result='EN_ATTENTE').count()
    examens_a_venir = Examen.objects.filter(date__gte=today).count()
    examens_blancs = Examen.objects.filter(type_examen='BLANC').count()
    
    # Apprenants concernés
    apprenants_concernes = Examen.objects.values('apprenant').distinct().count()
    
    # Taux de réussite
    total_avec_resultat = Examen.objects.exclude(result__in=['EN_ATTENTE', 'ABSENT']).count()
    total_admis = Examen.objects.filter(result='ADMIS').count()
    taux_reussite = round((total_admis / total_avec_resultat * 100) if total_avec_resultat > 0 else 0)
    
    # Activités récentes (exemples - à adapter selon votre logique)
    activites_recentes = []
    derniers_examens = Examen.objects.order_by('-date_creation')[:5]
    
    for examen in derniers_examens:
        activites_recentes.append({
            'icone': 'car' if examen.type_examen == 'CONDUITE' else 'pencil-alt',
            'titre': f"{examen.apprenant} - {examen.get_type_examen_display()}",
            'heure': f"Il y a {examen.date_creation.strftime('%H:%M')}",
            'statut': examen.get_result_display(),
            'statut_classe': examen.statut_examen_classe
        })
    
    context = {
        'total_examens': total_examens,
        'examens_aujourdhui': examens_aujourdhui,
        'examens_en_attente': examens_en_attente,
        'examens_non_payes': examens_non_payes,
        'examens_avec_resultats': examens_avec_resultats,
        'examens_a_venir': examens_a_venir,
        'examens_blancs': examens_blancs,
        'apprenants_concernes': apprenants_concernes,
        'taux_reussite': taux_reussite,
        'activites_recentes': activites_recentes,
    }
    
    return render(request, 'examens/hub.html', context)
    
@admin_required
def activites(request):
    """
    Vue détaillée de toutes les activités récentes liées aux examens
    """
    examens = Examen.objects.select_related('apprenant').order_by('-date_creation')[:50]
    
    activites_liste = []
    for examen in examens:
        activites_liste.append({
            'icone': 'car' if examen.type_examen == 'CONDUITE' else 'pencil-alt',
            'titre': f"{examen.apprenant} - {examen.get_type_examen_display()}",
            'heure': examen.date_creation,
            'statut': examen.get_result_display(),
            'statut_classe': examen.statut_examen_classe,
            'description': f"Examen prévu le {examen.date.strftime('%d/%m/%Y')} à {examen.heure_debut.strftime('%H:%M')}"
        })
    
    return render(request, 'examens/activites.html', {'activites': activites_liste})

@admin_required
def planning(request):
    """
    Vue calendrier/planning des examens à venir
    """
    today = timezone.now().date()
    examens_a_venir = Examen.objects.filter(date__gte=today).select_related('apprenant', 'moniteur', 'vehicule', 'seance').order_by('date', 'heure_debut')
    
    # Grouper par date pour un affichage plus clair si nécessaire
    planning_data = {}
    for examen in examens_a_venir:
        if examen.date not in planning_data:
            planning_data[examen.date] = []
        planning_data[examen.date].append(examen)
    
    return render(request, 'examens/planning.html', {
        'examens': examens_a_venir,
        'planning_data': planning_data
    })

@admin_required
def statistiques(request):
    """
    Vue détaillée des statistiques d'examens
    """
    total_examens = Examen.objects.count()
    total_admis = Examen.objects.filter(result='ADMIS').count()
    total_ajourne = Examen.objects.filter(result='AJOURNE').count()
    total_absent = Examen.objects.filter(result='ABSENT').count()
    total_attente = Examen.objects.filter(result='EN_ATTENTE').count()

    # Taux de réussite global (basé sur ceux qui ont un résultat définitif)
    total_evalues = total_admis + total_ajourne
    taux_global = round((total_admis / total_evalues * 100) if total_evalues > 0 else 0)

    # Statistiques par type d'examen
    stats_type = Examen.objects.values('type_examen').annotate(
        total=Count('id'),
        admis=Count('id', filter=Q(result='ADMIS')),
        ajourne=Count('id', filter=Q(result='AJOURNE')),
    )
    
    for s in stats_type:
        ev = s['admis'] + s['ajourne']
        s['taux'] = round((s['admis'] / ev * 100) if ev > 0 else 0)

    # Statistiques par moniteur (top 5)
    stats_moniteur = Examen.objects.filter(moniteur__isnull=False).values(
        'moniteur__nom', 'moniteur__prenom'
    ).annotate(
        total=Count('id'),
        admis=Count('id', filter=Q(result='ADMIS')),
    ).order_by('-total')[:5]

    for s in stats_moniteur:
        s['taux'] = round((s['admis'] / s['total'] * 100) if s['total'] > 0 else 0)

    context = {
        'total_examens': total_examens,
        'total_admis': total_admis,
        'total_ajourne': total_ajourne,
        'total_absent': total_absent,
        'total_attente': total_attente,
        'taux_global': taux_global,
        'stats_type': stats_type,
        'stats_moniteur': stats_moniteur,
    }
    
    return render(request, 'examens/statistiques.html', context)

@admin_required
def examen_export(request):
    """
    Exporte la liste des examens en CSV avec les filtres appliqués
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="examens_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Heure', 'Apprenant', 'Type', 'Moniteur', 'Véhicule', 'Résultat', 'Payé'])
    
    examens = Examen.objects.select_related('apprenant', 'moniteur', 'vehicule').all()
    
    # Appliquer les mêmes filtres que dans la liste
    examen_type = request.GET.get('type')
    resultat = request.GET.get('resultat')
    periode = request.GET.get('periode')
    apprenant_query = request.GET.get('apprenant')
    
    if examen_type:
        examens = examens.filter(type_examen=examen_type)
    if resultat:
        examens = examens.filter(result=resultat)
    if apprenant_query:
        examens = examens.filter(
            Q(apprenant__nom__icontains=apprenant_query) | 
            Q(apprenant__prenom__icontains=apprenant_query)
        )
    if periode:
        today = timezone.now().date()
        if periode == 'aujourdhui':
            examens = examens.filter(date=today)
        elif periode == 'semaine':
            start_week = today - timedelta(days=today.weekday())
            examens = examens.filter(date__gte=start_week)
        elif periode == 'mois':
            examens = examens.filter(date__month=today.month, date__year=today.year)

    for examen in examens:
        writer.writerow([
            examen.date.strftime('%d/%m/%Y'),
            examen.heure_debut.strftime('%H:%M'),
            f"{examen.apprenant.prenom} {examen.apprenant.nom}",
            examen.get_type_examen_display(),
            f"{examen.moniteur.prenom} {examen.moniteur.nom}" if examen.moniteur else "N/A",
            str(examen.vehicule) if examen.vehicule else "N/A",
            examen.get_result_display(),
            "Oui" if examen.est_paye else "Non"
        ])
        
    return response

# Liste des examens
@admin_required
def examen_list(request):
    examens = Examen.objects.select_related('apprenant', 'moniteur', 'vehicule', 'seance').all()
    
    # Appliquer les filtres
    examen_type = request.GET.get('type')
    resultat = request.GET.get('resultat')
    periode = request.GET.get('periode')
    apprenant_query = request.GET.get('apprenant')
    
    if examen_type:
        examens = examens.filter(type_examen=examen_type)
    if resultat:
        examens = examens.filter(result=resultat)
    if apprenant_query:
        examens = examens.filter(
            Q(apprenant__nom__icontains=apprenant_query) | 
            Q(apprenant__prenom__icontains=apprenant_query)
        )
    if periode:
        today = timezone.now().date()
        if periode == 'aujourdhui':
            examens = examens.filter(date=today)
        elif periode == 'semaine':
            start_week = today - timedelta(days=today.weekday())
            examens = examens.filter(date__gte=start_week)
        elif periode == 'mois':
            examens = examens.filter(date__month=today.month, date__year=today.year)

    # Statistiques pour les mini-cartes
    stats = {
        'total': examens.count(),
        'admis': examens.filter(result='ADMIS').count(),
        'en_attente': examens.filter(result='EN_ATTENTE').count(),
        'non_payes': examens.filter(est_paye=False).count(),
    }

    context = {
        'examens': examens,
        'type_choices': EXAM_TYPE_CHOICES,
        'result_choices': RESULT_CHOICES,
        'stats': stats,
    }
    return render(request, 'examens/examen_list.html', context)

# Créer un examen
@admin_required
def examen_create(request):
    if request.method == 'POST':
        form = ExamenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Examen créé avec succès.")
            return redirect('examens:examen_list')
    else:
        form = ExamenForm()
    return render(request, 'examens/examen_form.html', {'form': form, 'action': 'Créer'})

# Modifier un examen
@admin_required
def examen_update(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    if request.method == 'POST':
        form = ExamenForm(request.POST, instance=examen)
        if form.is_valid():
            form.save()
            messages.success(request, "Examen mis à jour avec succès.")
            return redirect('examens:examen_list')
    else:
        form = ExamenForm(instance=examen)
    # Provide the examen instance in context so the template can access its pk and recap
    return render(request, 'examens/examen_form.html', {
        'form': form,
        'action': 'Modifier',
        'examen': examen,
        'object': examen,
    })

# Valider un examen (saisie résultat)
@admin_required
def examen_validate(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    
    if request.method == 'POST':
        form = ExamenResultForm(request.POST, instance=examen)
        if form.is_valid():
            try:
                # La méthode save du modèle appellera full_clean()
                # qui contient la validation de paiement
                form.save()
                messages.success(request, f"Résultat enregistré pour {examen.apprenant}.")
                return redirect('examens:examen_list')
            except ValidationError as e:
                # Capturer les erreurs de validation du modèle (ex: non payé)
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, error)
            except Exception as e:
                messages.error(request, f"Erreur : {str(e)}")
    else:
        form = ExamenResultForm(instance=examen)
    
    return render(request, 'examens/examen_validate.html', {
        'form': form, 
        'examen': examen
    })

# Enregistrer le paiement
@admin_required
def examen_paiement(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    examen.est_paye = True
    examen.save()
    messages.success(request, f"Paiement enregistré pour {examen.apprenant}.")
    return redirect('examens:examen_detail', pk=pk)

# Imprimer l'examen
@admin_required
def examen_print(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    return render(request, 'examens/examen_print.html', {'examen': examen})

# Détail d’un examen
@admin_required
def examen_detail(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    return render(request, 'examens/examen_detail.html', {'examen': examen})

# Supprimer un examen
@admin_required
def examen_delete(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    if request.method == 'POST':
        examen.delete()
        messages.success(request, "Examen supprimé avec succès.")
        return redirect('examens:examen_list')
    return render(request, 'examens/examen_confirm_delete.html', {'examen': examen})
