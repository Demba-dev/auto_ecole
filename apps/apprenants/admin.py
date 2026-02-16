from django.contrib import admin
from .models import (
    TypePermis,
    Apprenant,
    DossierApprenant,
    ProgressionConduite
)


@admin.register(TypePermis)
class TypePermisAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle')


class DossierInline(admin.StackedInline):
    model = DossierApprenant
    extra = 0


class ProgressionInline(admin.StackedInline):
    model = ProgressionConduite
    extra = 0


@admin.register(Apprenant)
class ApprenantAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'telephone', 'date_inscription', 'actif')
    search_fields = ('nom', 'prenom', 'telephone')
    list_filter = ('actif', 'types_permis')

    inlines = [DossierInline, ProgressionInline]
