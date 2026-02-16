from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contrat
from apps.apprenants.models import ProgressionConduite


@receiver(post_save, sender=Contrat)
def update_progression_conduite(sender, instance, created, **kwargs):
    """
    Met à jour automatiquement les heures achetées dans ProgressionConduite
    lorsque qu'un contrat est créé ou modifié.
    """
    apprenant = instance.apprenant
    progression, _ = ProgressionConduite.objects.get_or_create(apprenant=apprenant)

    # Met à jour les heures achetées en cumulant tous les contrats actifs
    total_heures = sum(c.heures_inclues for c in apprenant.contrats.all())
    progression.heures_achetees = total_heures

    # On peut recalculer les heures restantes si nécessaire
    progression.save()
