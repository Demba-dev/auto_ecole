from django.contrib import admin
from .models import Tarif, Contrat, Paiement


@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = ('type_permis', 'libelle', 'montant', 'heures_inclues', 'actif')
    list_filter = ('type_permis', 'actif')
    search_fields = ('type_permis', 'libelle')


class PaiementInline(admin.TabularInline):
    model = Paiement
    extra = 0


@admin.register(Contrat)
class ContratAdmin(admin.ModelAdmin):
    list_display = ('apprenant', 'tarif', 'montant_total', 'heures_inclues', 'heures_effectuees', 'montant_restant')
    inlines = [PaiementInline]
    search_fields = ('apprenant__nom', 'apprenant__prenom')
