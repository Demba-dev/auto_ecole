from django.contrib import admin
from .models import Examen
from apps.apprenants.models import Apprenant
from apps.accounts.models import User
from apps.vehicules.models import Vehicule

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = (
        'type_examen',
        'date',
        'heure_debut',
        'heure_fin',
        'apprenant',
        'moniteur',
        'vehicule',
        'result'
    )
    
    list_filter = (
        'type_examen',
        'result',
        'date',
        'moniteur',
        'vehicule',
    )

    search_fields = (
        'apprenant__nom',
        'apprenant__prenom',
        'moniteur__first_name',
        'moniteur__last_name',
        'vehicule__immatriculation',
    )

    readonly_fields = ('date_creation', 'heure_fin')
