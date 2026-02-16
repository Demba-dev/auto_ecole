from django.db import models
from apps.apprenants.models import Apprenant
from apps.accounts.models import User
from apps.vehicules.models import Vehicule
from datetime import datetime, timedelta

EXAM_TYPE_CHOICES = [
    ('CODE', 'Épreuve théorique'),
    ('CONDUITE', 'Épreuve pratique'),
]

RESULT_CHOICES = [
    ('ADMIS', 'Admis'),
    ('AJOURNE', 'Ajourné'),
    ('ABSENT', 'Absent'),
]

class Examen(models.Model):
    type_examen = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    date = models.DateField()
    heure_debut = models.TimeField()
    duree_minutes = models.PositiveIntegerField(default=60)

    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='examens')
    moniteur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='examens', limit_choices_to={'role': 'MONITEUR'}
    )
    vehicule = models.ForeignKey(
        Vehicule, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='examens'
    )

    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='ABSENT')
    notes = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'heure_debut']
        unique_together = ('apprenant', 'date', 'heure_debut', 'type_examen')

    @property
    def heure_fin(self):
        debut = datetime.combine(self.date, self.heure_debut)
        fin = debut + timedelta(minutes=self.duree_minutes)
        return fin.time()

    def __str__(self):
        return f"{self.get_type_examen_display()} - {self.apprenant} le {self.date} à {self.heure_debut}"
