from django.contrib import admin
from .models import (
    Employe,
    MoniteurProfile,
    AffectationMoniteur,
    DisponibiliteMoniteur
)


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'type_employe',
        'telephone',
        'date_embauche',
        'actif',
    )
    list_filter = ('type_employe', 'actif')
    search_fields = ('user__username', 'telephone')
    ordering = ('type_employe',)


@admin.register(MoniteurProfile)
class MoniteurProfileAdmin(admin.ModelAdmin):
    list_display = (
        'employe',
        'numero_agrement',
        'taux_horaire',
    )
    filter_horizontal = ('specialites',)
    search_fields = ('employe__user__username', 'numero_agrement')


@admin.register(AffectationMoniteur)
class AffectationMoniteurAdmin(admin.ModelAdmin):
    list_display = (
        'apprenant',
        'moniteur',
        'date_debut',
        'actif',
    )
    list_filter = ('actif',)
    search_fields = (
        'apprenant__nom',
        'apprenant__prenom',
        'moniteur__user__username',
    )


@admin.register(DisponibiliteMoniteur)
class DisponibiliteMoniteurAdmin(admin.ModelAdmin):
    list_display = (
        'moniteur',
        'jour_semaine',
        'heure_debut',
        'heure_fin',
        'actif',
    )
    list_filter = ('jour_semaine', 'actif')
    search_fields = ('moniteur__user__username',)
