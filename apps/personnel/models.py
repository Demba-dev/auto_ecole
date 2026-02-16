from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.apprenants.models import TypePermis, Apprenant


class Employe(models.Model):
    TYPE_CHOICES = [
        ('MONITEUR', 'Moniteur'),
        ('ADMIN', 'Administratif'),
        ('DIRECTION', 'Direction'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employe'
    )

    nom = models.CharField(max_length=100, default='')
    prenom = models.CharField(max_length=100, default='')
    email = models.EmailField(blank=True, null=True)

    type_employe = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    telephone = models.CharField(max_length=20)
    date_embauche = models.DateField()
    actif = models.BooleanField(default=True)

    def __str__(self):
        nom_complet = f"{self.prenom} {self.nom}".strip()
        if not nom_complet and self.user:
            nom_complet = self.user.username
        return f"{nom_complet} - {self.get_type_employe_display()}"


class MoniteurProfile(models.Model):
    employe = models.OneToOneField(
        Employe,
        on_delete=models.CASCADE,
        related_name='profil_moniteur'
    )

    numero_agrement = models.CharField(
        max_length=100,
        unique=True
    )

    specialites = models.ManyToManyField(
        TypePermis,
        related_name='moniteurs'
    )

    taux_horaire = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def __str__(self):
        return str(self.employe)


class AffectationMoniteur(models.Model):
    apprenant = models.ForeignKey(
        Apprenant,
        on_delete=models.CASCADE,
        related_name='affectations'
    )

    moniteur = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        limit_choices_to={'type_employe': 'MONITEUR'},
        related_name='affectations_apprenants'
    )

    date_debut = models.DateField(default=timezone.now)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.apprenant} → {self.moniteur}"


class DisponibiliteMoniteur(models.Model):
    JOURS = [
        (1, 'Lundi'),
        (2, 'Mardi'),
        (3, 'Mercredi'),
        (4, 'Jeudi'),
        (5, 'Vendredi'),
        (6, 'Samedi'),
        (7, 'Dimanche'),
    ]

    moniteur = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        limit_choices_to={'type_employe': 'MONITEUR'},
        related_name='disponibilites'
    )

    jour_semaine = models.PositiveSmallIntegerField(choices=JOURS)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    actif = models.BooleanField(default=True)

    def clean(self):
        if self.heure_fin <= self.heure_debut:
            raise ValidationError("L'heure de fin doit être après l'heure de début")

    def __str__(self):
        return f"{self.moniteur} - {self.get_jour_semaine_display()}"
