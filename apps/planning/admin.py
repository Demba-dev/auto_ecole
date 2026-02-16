from django.contrib import admin
from .models import Seance


@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ('type_seance', 'date', 'heure_debut', 'apprenant', 'moniteur', 'vehicule', 'statut')
    list_filter = ('type_seance', 'statut', 'date')
    search_fields = ('apprenant__nom', 'apprenant__prenom', 'moniteur__first_name', 'moniteur__last_name')
