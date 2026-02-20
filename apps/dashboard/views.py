# views.py
from django.shortcuts import render
from apps.accounts.decorators import admin_required
from django.utils import timezone
from django.db.models import Count, Sum, Q
from apps.apprenants.models import Apprenant
from apps.personnel.models import Employe
from apps.planning.models import Seance
from apps.examens.models import Examen
from apps.finance.models import Paiement, Contrat
from django.urls import reverse
from apps.vehicules.models import Vehicule
from datetime import date, timedelta
from collections import defaultdict
import calendar


# === OBJECTIFS helpers ===
def get_objectifs_mois():
    """Retourne les objectifs du mois pour les métriques clefs.
    En production ces valeurs viendraient d'une table ou d'un paramètre.
    """
    return {
        'seances': 150,           # objectif séance
        'ca': 2000000,            # objectif chiffre d'affaires
    }


def build_objectifs_context(today):
    """Calcule le pourcentage de réalisation des objectifs du mois."""
    first_day = today.replace(day=1)
    seances_count = Seance.objects.filter(date__gte=first_day).count()
    ca_count = Paiement.objects.filter(date_paiement__gte=first_day).aggregate(total=Sum('montant'))['total'] or 0
    obj = get_objectifs_mois()
    return {
        'objectif_seances': obj['seances'],
        'objectif_ca': obj['ca'],
        'progress_seances': min(int(seances_count * 100 / obj['seances']) if obj['seances'] else 0, 100),
        'progress_ca': min(int(ca_count * 100 / obj['ca']) if obj['ca'] else 0, 100),
        'seances_count': seances_count,
        'ca_count': ca_count,
    }


@admin_required
def dashboard(request):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_month = today.replace(day=1) - timedelta(days=1)
    first_day_of_last_month = last_month.replace(day=1)
    
    ca_mois = Paiement.objects.filter(date_paiement__gte=first_day_of_month).aggregate(total=Sum('montant'))['total'] or 0
    ca_mois_precedent = Paiement.objects.filter(
        date_paiement__gte=first_day_of_last_month,
        date_paiement__lt=first_day_of_month
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Statistiques générales avec filtres temporels
    context = {
        # === CARTES STATISTIQUES PRINCIPALES ===
        "total_apprenants": Apprenant.objects.count(),
        "apprenants_actifs": Apprenant.objects.filter(actif=True).count(),
        "nouveaux_apprenants_mois": Apprenant.objects.filter(date_inscription__gte=first_day_of_month).count(),
        
        "total_moniteurs": Employe.objects.filter(type_employe="MONITEUR").count(),
        "moniteurs_actifs": Employe.objects.filter(type_employe="MONITEUR", actif=True).count(),
        
        "total_seances": Seance.objects.count(),
        "seances_mois": Seance.objects.filter(date__gte=first_day_of_month).count(),
        "seances_jour": Seance.objects.filter(date=today).count(),
        
        "total_examens": Examen.objects.count(),
        "examens_mois": Examen.objects.filter(date__gte=first_day_of_month).count(),
        "examens_impayes": Examen.objects.filter(est_paye=False).count(),
        
        "total_vehicules": Vehicule.objects.count(),
        "vehicules_disponibles": Vehicule.objects.filter(statut='DISPONIBLE').count(),
        "vehicules_maintenance": Vehicule.objects.filter(statut='MAINTENANCE').count(),
        
        # === FINANCES ===
        "ca_mois": ca_mois,
        "ca_mois_precedent": ca_mois_precedent,
        "ca_variation": calculate_variation(ca_mois_precedent, ca_mois),
        
        "contrats_impayes": Contrat.objects.avec_stats().filter(montant_restant__gt=0).count(),
        "total_impayes": Contrat.objects.avec_stats().aggregate(total=Sum('montant_restant'))['total'] or 0,
        
        # === SÉANCES ===
        "seances_today": Seance.objects.filter(date=today).select_related('apprenant', 'moniteur')[:8],
        "seances_a_venir": Seance.objects.filter(date__gte=today, statut='PREVU').order_by('date', 'heure_debut')[:5],
        "seances_par_statut": Seance.objects.values('statut').annotate(count=Count('id')),
        
        # === EXAMENS À VENIR ===
        "examens_a_venir": Examen.objects.filter(date__gte=today).order_by('date')[:5],
        
        # === QUICK ACTIONS ===
        "quick_actions": [
            {"label": "Ajouter apprenant", "url": reverse('apprenants:ajouter_apprenant'), "icon": "user-plus"},
            {"label": "Nouvelle séance", "url": reverse('planning:seance_create'), "icon": "calendar-plus"},
            {"label": "Créer examen", "url": reverse('examens:examen_create'), "icon": "graduation-cap"},
            {"label": "Ajouter véhicule", "url": reverse('vehicules:vehicule_create'), "icon": "car"},
            {"label": "Encaisser paiement", "url": reverse('finance:paiement_create'), "icon": "credit-card"},
        ],
        
        # === STATISTIQUES HEBDOMADAIRES ===
        # zip returns tuples; template expects objects with .nom and .count keys
        # build weekly stats and hide when every day has zero sessions
        "stats_hebdo": (lambda data: [] if all(d['count'] == 0 for d in data) else data)([
            {"nom": jour["nom"], "count": cnt}
            for jour, cnt in zip(get_semaine_jours(), get_seances_semaine())
        ]),
        # === OBJECTIFS / PERFORMANCES ===
        # will update below after initial context
        
        # === TOP PERFORMANCES ===
        "top_moniteurs": get_top_moniteurs(),
        "apprenants_avec_examens": Apprenant.objects.filter(examens__isnull=False).distinct().count(),
        
        # === TAUX DE RÉUSSITE ===
        "taux_reussite": get_taux_reussite(),
        "taux_reussite_offset": 326.56 * (1 - get_taux_reussite() / 100),
        
        # === ALERTES ===
        "alertes": get_alertes(),
    }

    # Calcul des variations pour les KPIs
    context['variation_apprenants'] = calculate_variation(
        Apprenant.objects.filter(date_inscription__lt=first_day_of_month).count(),
        context['nouveaux_apprenants_mois']
    )
    # merge objectifs data
    context.update(build_objectifs_context(today))
    
    return render(request, "dashboard/dashboard.html", context)

# === OBJECTIFS helpers ===
def get_objectifs_mois():
    """Retourne les objectifs du mois pour les métriques clefs.
    En production ces valeurs viendraient d'une table ou d'un paramètre.
    """
    return {
        'seances': 150,           # objectif séance
        'ca': 2000000,            # objectif chiffre d'affaires
    }


def build_objectifs_context(today):
    """Calcule le pourcentage de réalisation des objectifs du mois."""
    first_day = today.replace(day=1)
    seances_count = Seance.objects.filter(date__gte=first_day).count()
    ca_count = Paiement.objects.filter(date_paiement__gte=first_day).aggregate(total=Sum('montant'))['total'] or 0
    obj = get_objectifs_mois()
    return {
        'objectif_seances': obj['seances'],
        'objectif_ca': obj['ca'],
        'progress_seances': min(int(seances_count * 100 / obj['seances']) if obj['seances'] else 0, 100),
        'progress_ca': min(int(ca_count * 100 / obj['ca']) if obj['ca'] else 0, 100),
        'seances_count': seances_count,
        'ca_count': ca_count,
    }

# end of build_objectifs_context

def get_semaine_jours():
    """Retourne les 7 derniers jours avec leur nom"""
    jours = []
    today = date.today()
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        jours.append({
            'date': d,
            'nom': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][d.weekday()],
            'jour': d.day
        })
    return jours

def get_seances_semaine():
    """Compte les séances par jour pour les 7 derniers jours"""
    result = []
    today = date.today()
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        count = Seance.objects.filter(date=d).count()
        result.append(count)
    return result

def get_top_moniteurs(limit=3):
    """Retourne les moniteurs avec le plus de séances"""
    return Employe.objects.filter(type_employe='MONITEUR').annotate(
        nb_seances=Count('seances')
    ).order_by('-nb_seances')[:limit]

def get_taux_reussite():
    """Calcule le taux de réussite aux examens"""
    total = Examen.objects.count()
    if total == 0:
        return 0
    reussis = Examen.objects.filter(result='ADMIS').count()
    return round((reussis / total) * 100, 1)

def get_alertes():
    """Génère les alertes pour le dashboard"""
    alertes = []
    today = date.today()
    
    # Maintenances à venir
    from apps.vehicules.models import Maintenance
    maintenances = Maintenance.objects.filter(
        prochaine_echeance__gte=today,
        prochaine_echeance__lte=today + timedelta(days=7)
    ).select_related('vehicule')
    
    for m in maintenances:
        alertes.append({
            'type': 'warning',
            'icone': 'tools',
            'titre': f"Maintenance {m.vehicule}",
            'message': f"{m.type_maintenance} prévue le {m.prochaine_echeance.strftime('%d/%m')}",
            'lien': f"/vehicules/maintenance/{m.id}/"
        })
    
    # Impayés importants
    contrats = Contrat.objects.avec_stats().filter(montant_restant__gt=100000).select_related('apprenant')[:3]
    for c in contrats:
        alertes.append({
            'type': 'danger',
            'icone': 'exclamation-triangle',
            'titre': f"Impayé {c.apprenant}",
            'message': f"Solde de {c.montant_restant} FCFA",
            'lien': f"/finance/contrat/{c.id}/"
        })
    
    # Examens non payés
    examens = Examen.objects.filter(est_paye=False, date__gte=today)[:3]
    for e in examens:
        alertes.append({
            'type': 'info',
            'icone': 'info-circle',
            'titre': f"Examen non payé",
            'message': f"{e.apprenant} - {e.date.strftime('%d/%m')}",
            'lien': f"/examens/{e.id}/"
        })
    
    return alertes

def calculate_variation(ancien, nouveau):
    """Calcule la variation en pourcentage"""
    if ancien == 0:
        return 100 if nouveau > 0 else 0
    variation = ((nouveau - ancien) / ancien) * 100
    return round(variation, 1)