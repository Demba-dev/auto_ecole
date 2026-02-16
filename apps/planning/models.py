from django.db import models
from apps.apprenants.models import Apprenant
from apps.accounts.models import User  # Moniteurs
from apps.vehicules.models import Vehicule  # On créera ce module après si pas encore
from datetime import timedelta, datetime

SESSION_TYPE_CHOICES = [
    ('CODE', 'Cours de code'),
    ('CONDUITE', 'Leçon de conduite'),
    ('EXAMEN', 'Examen blanc'),
    ('RATTRAPAGE', 'Séance de rattrapage'),
]

STATUS_CHOICES = [
    ('PREVU', 'Prévu'),
    ('REALISE', 'Réalisé'),
    ('ANNULE', 'Annulé'),
    ('ABSENT', 'Absent'),
    ('REPORTE', 'Reporté'),
]


class Seance(models.Model):
    type_seance = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    date = models.DateField()
    heure_debut = models.TimeField()
    duree_minutes = models.PositiveIntegerField(default=60)
    
    apprenant = models.ForeignKey(
        Apprenant, on_delete=models.CASCADE, related_name='seances'
    )
    moniteur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='seances', limit_choices_to={'role': 'MONITEUR'}
    )
    vehicule = models.ForeignKey(
        'vehicules.Vehicule', on_delete=models.SET_NULL, related_name='seances', null=True, blank=True
    )

    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PREVU')
    compte_rendu = models.TextField(blank=True, null=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'heure_debut']
        unique_together = ('apprenant', 'date', 'heure_debut')  # évite doublon exact

    def __str__(self):
        return f"{self.get_type_seance_display()} - {self.apprenant} avec {self.moniteur} le {self.date} à {self.heure_debut}"
    
    @property
    def heure_fin(self):
        debut = datetime.combine(self.date, self.heure_debut)
        fin = debut + timedelta(minutes=self.duree_minutes)
        return fin.time()
    
    def save(self, *args, **kwargs):
        # Vérification conflit moniteur
        conflits_moniteur = Seance.objects.filter(
            moniteur=self.moniteur,
            date=self.date,
            heure_debut=self.heure_debut
        ).exclude(id=self.id)
        if conflits_moniteur.exists():
            raise ValueError("Ce moniteur est déjà occupé à cette heure.")

        # Vérification conflit véhicule
        if self.vehicule:
            conflits_vehicule = Seance.objects.filter(
                vehicule=self.vehicule,
                date=self.date,
                heure_debut=self.heure_debut
            ).exclude(id=self.id)
            if conflits_vehicule.exists():
                raise ValueError("Ce véhicule est déjà réservé à cette heure.")

        super().save(*args, **kwargs)
