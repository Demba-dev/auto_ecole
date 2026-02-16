from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        GESTIONNAIRE = 'GESTIONNAIRE', 'Gestionnaire'
        MONITEUR = 'MONITEUR', 'Moniteur'
        APPRENANT = 'APPRENANT', 'Apprenant'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.APPRENANT
    )

    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    photo = models.ImageField(
        upload_to='users/photos/',
        blank=True,
        null=True
    )

    is_deleted = models.BooleanField(
        default=False,
        help_text="Suppression logique (RGPD)"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
