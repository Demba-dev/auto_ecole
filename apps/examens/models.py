from django.db import models
from django.core.exceptions import ValidationError
from apps.apprenants.models import Apprenant
from apps.personnel.models import Employe
from apps.vehicules.models import Vehicule
from django.utils import timezone
from apps.planning.models import Seance
from datetime import timedelta, datetime



EXAM_TYPE_CHOICES = [
    ('CODE', 'Épreuve théorique'),
    ('CONDUITE', 'Épreuve pratique'),
]

RESULT_CHOICES = [
    ('EN_ATTENTE', 'En attente'),
    ('ADMIS', 'Admis'),
    ('AJOURNE', 'Ajourné'),
    ('ABSENT', 'Absent'),
]


class Examen(models.Model):
    type_examen = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    date = models.DateField(default=timezone.now)
    heure_debut = models.TimeField()
    duree_minutes = models.PositiveIntegerField(default=60)

    seance = models.OneToOneField(
        Seance,
        on_delete=models.CASCADE,
        related_name='examen'
    )

    apprenant = models.ForeignKey(
        Apprenant,
        on_delete=models.CASCADE,
        related_name='examens'
    )

    moniteur = models.ForeignKey(
        Employe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='examens',
        limit_choices_to={'type_employe':'MONITEUR'}
    )

    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='examens'
    )

    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default='EN_ATTENTE'
    )

    notes = models.TextField(blank=True, null=True)

    tentative = models.PositiveIntegerField(default=1)

    date_creation = models.DateTimeField(auto_now_add=True)
    est_paye = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_creation']

    @property
    def heure_fin(self):
        debut = datetime.combine(self.date, self.heure_debut)
        fin = debut + timedelta(minutes=self.duree_minutes)
        return fin.time()
    
    @property
    def est_passe(self):
        """Vérifie si l'examen est déjà passé"""
        maintenant = timezone.now()
        date_heure_examen = datetime.combine(self.date, self.heure_debut)
        return timezone.make_aware(date_heure_examen) < maintenant

    @property
    def est_aujourdhui(self):
        """Vérifie si l'examen est aujourd'hui"""
        return self.date == timezone.now().date()

    @property
    def statut_paiement_classe(self):
        """Retourne la classe CSS pour le statut de paiement"""
        return "success" if self.est_paye else "warning"

    @property
    def statut_examen_classe(self):
        """Retourne la classe CSS pour le statut de l'examen"""
        classes = {
            'ADMIS': 'success',
            'AJOURNE': 'danger',
            'EN_ATTENTE': 'warning',
            'ABSENT': 'secondary'
        }
        return classes.get(self.result, 'secondary')

    

    def clean(self):

        #Vérifier que la séance est bien de type EXAMEN
        if self.seance.type_seance != "EXAMEN":
            raise ValidationError("La séance liée doit être de type EXAMEN.")

        # Vérifier cohérence apprenant
        if self.seance.apprenant != self.apprenant:
            raise ValidationError("L’apprenant ne correspond pas à celui de la séance.")
        
        # Empecher la validation si non payé
        if self.result in ["ADMIS", "AJOURNE"] and not self.est_paye:
            raise ValidationError("Le paiement doit être effectué pour valider le résultat.")

    def save(self, *args, **kwargs):

        if not self.pk:
            last = Examen.objects.filter(
                apprenant=self.apprenant,
                seance__type_seance=self.seance.type_seance
            ).order_by('-tentative').first()

            if last:
                self.tentative = last.tentative + 1

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Examen - {self.apprenant} ({self.get_result_display()})"
