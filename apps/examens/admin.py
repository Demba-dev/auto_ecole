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
        'get_heure_fin',
        'apprenant',
        'moniteur',
        'vehicule',
        'result',
        'est_paye',
        'date_creation',
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
        'moniteur__username',
        'vehicule__immatriculation',
    )

    readonly_fields = ('date_creation', 'get_heure_fin')

    def get_heure_fin(self, obj):
        return obj.heure_fin
    get_heure_fin.short_description = 'Heure de fin'