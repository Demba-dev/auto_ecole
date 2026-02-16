from django.db import models
from django.utils import timezone

STATUS_CHOICES = [
    ('DISPONIBLE', 'Disponible'),
    ('OCCUPE', 'Occupé'),
    ('MAINTENANCE', 'Maintenance'),
    ('INDISPONIBLE', 'Indisponible'),
]

class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=50, default="")
    modele = models.CharField(max_length=50, default="")
    type_boite = models.CharField(max_length=20, choices=[('MANUELLE','Manuelle'),('AUTOMATIQUE','Automatique')], default='MANUELLE')
    energie = models.CharField(max_length=20, choices=[('ESSENCE','Essence'),('DIESEL','Diesel'),('ELECTRIQUE','Électrique')], default='ESSENCE')
    kilometrage_initial = models.PositiveIntegerField(default=0)
    date_mise_circulation = models.DateField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DISPONIBLE')

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.immatriculation})"


class Maintenance(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='maintenances')
    date = models.DateField(default=timezone.now)
    type_maintenance = models.CharField(max_length=100)  # Vidange, Réparation, Pneus…
    kilometrage = models.PositiveIntegerField()
    prestataire = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    prochaine_echeance = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.vehicule} - {self.type_maintenance} le {self.date}"
