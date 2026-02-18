from django.db import models
from django.utils import timezone
from apps.apprenants.models import Apprenant, TypePermis
from django.db.models import Sum, F
from django.core.exceptions import ValidationError
from django.db.models.functions import Coalesce
from django.db.models import Value


class Tarif(models.Model):
    type_permis = models.ForeignKey(
        TypePermis,
        on_delete=models.PROTECT,
        related_name="tarifs"
    )
  # B, A, C...
    libelle = models.CharField(max_length=100)     # Exemple : "Forfait 20h"
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    heures_inclues = models.PositiveIntegerField(default=0)  # Pour conduite
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.type_permis} - {self.libelle} ({self.montant} FCFA)"


class ContratQuerySet(models.QuerySet):
    def avec_stats(self):
        return self.annotate(
            total_paye=Coalesce(Sum('paiements__montant'), Value(0, output_field=models.DecimalField()))
        ).annotate(
            montant_restant=F('montant_total') - F('total_paye')
        )

class Contrat(models.Model):
    apprenant = models.ForeignKey(
        Apprenant,
        on_delete=models.CASCADE,
        related_name="contrats"
    )
    tarif = models.ForeignKey(
        Tarif,
        on_delete=models.PROTECT,
        related_name="contrats"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateField(blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    heures_inclues = models.PositiveIntegerField(default=0)
    heures_effectuees = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    objects = ContratQuerySet.as_manager()

    def __str__(self):
        return f"Contrat {self.apprenant} - {self.tarif}"

    @property
    def solde_heures(self):
        return max(self.heures_inclues - self.heures_effectuees, 0)

    @property
    def montant_paye(self):
        return self.paiements.aggregate(total=Sum('montant'))['total'] or 0

    @property
    def montant_restant(self):
        return max(self.montant_total - self.montant_paye, 0)

    @property
    def pourcentage_paiement(self):
        if self.montant_total > 0:
            return min(int((self.montant_paye / self.montant_total) * 100), 100)
        return 0


class Paiement(models.Model):
    MODE_CHOICES = [
        ('ESPECE', 'Espèces'),
        ('CHEQUE', 'Chèque'),
        ('VIREMENT', 'Virement'),
        ('MOBILE', 'Mobile Money')
    ]

    contrat = models.ForeignKey(
        Contrat,
        on_delete=models.CASCADE,
        related_name="paiements"
    )
    date_paiement = models.DateTimeField(default=timezone.now)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    reference = models.CharField(max_length=100, blank=True, null=True)  # N° chèque, transaction, etc.

    def save(self, *args, **kwargs):
        if not self.reference and self.date_paiement:
            date_str = self.date_paiement.strftime('%Y%m%d')
            import random
            rand_suffix = random.randint(100, 999)
            self.reference = f"PAY-{date_str}-{rand_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contrat.apprenant} - {self.montant} FCFA ({self.mode})"
    

class PaiementExamen(models.Model):

    examen = models.OneToOneField(
        'examens.Examen',
        on_delete=models.CASCADE,
        related_name='paiement'
    )

    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)
    mode = models.CharField(max_length=20, choices=Paiement.MODE_CHOICES)

    est_valide = models.BooleanField(default=True)


    def clean(self):
        if self.examen.est_paye:
            raise ValidationError("Ce paiement a déjà été validé pour cet examen.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.est_valide:
            self.examen.est_paye = True
            self.examen.save()

    def __str__(self):
        return f"{self.examen.apprenant} - {self.montant} FCFA (Examen)"

