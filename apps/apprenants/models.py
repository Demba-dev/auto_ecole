from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import date
from django.core.exceptions import ValidationError

class TypePermis(models.Model):
    code = models.CharField(max_length=10, unique=True)   # B, A, C...
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class Apprenant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='apprenant'
    )

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    types_permis = models.ManyToManyField(
        TypePermis,
        related_name='apprenants'
    )

    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20, 
        choices=[
            ('inscrit', 'Inscrit'),
            ('formation', 'En formation'),
            ('permis_obtenu', 'Permis obtenu'),
            ('abandon', 'Abandon'),
        ],
        default='inscrit'
    )
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def age(self):
        """Calcule l'âge de l'apprenant"""
        today = date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )
    
    def clean(self):
        """Validation métier"""
        if self.date_naissance:
            age = (date.today() - self.date_naissance).days / 365.25
            if age < 16:
                raise ValidationError("Âge minimum requis : 16 ans")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Décommentez pour activer validation
        super().save(*args, **kwargs)

    
        


class DossierApprenant(models.Model):
    apprenant = models.OneToOneField(
        Apprenant,
        on_delete=models.CASCADE,
        related_name='dossier'
    )

    numero_dossier = models.CharField(max_length=50, unique=True, editable=False)

    piece_identite = models.FileField(
        upload_to='apprenants/pieces/',
        blank=True,
        null=True
    )
    photo = models.ImageField(
        upload_to='apprenants/photos/',
        blank=True,
        null=True
    )
    certificat_medical = models.FileField(
        upload_to='apprenants/certificats/',
        blank=True,
        null=True
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.numero_dossier

    def save(self, *args, **kwargs):
        if not self.numero_dossier:
            # Génération automatique : KAL-2025-0001
            annee = timezone.now().year
            dernier = DossierApprenant.objects.filter(
                numero_dossier__startswith=f"KAL-{annee}"
            ).order_by('-numero_dossier').first()
            
            if dernier:
                dernier_num = int(dernier.numero_dossier.split('-')[-1])
                nouveau_num = dernier_num + 1
            else:
                nouveau_num = 1
                
            self.numero_dossier = f"KAL-{annee}-{nouveau_num:04d}"
        super().save(*args, **kwargs)


class ProgressionConduite(models.Model):
    apprenant = models.OneToOneField(
        Apprenant,
        on_delete=models.CASCADE,
        related_name='progression_conduite'
    )

    heures_achetees = models.PositiveIntegerField(default=0)
    heures_effectuees = models.PositiveIntegerField(default=0)

    @property
    def heures_restantes(self):
        return max(self.heures_achetees - self.heures_effectuees, 0)
    
    @property
    def pourcentage_progression(self):
        """Calcule le pourcentage de progression"""
        if self.heures_achetees > 0:
            return (self.heures_effectuees / self.heures_achetees) * 100
        return 0

    def __str__(self):
        return f"{self.apprenant} - {self.heures_restantes}h restantes"

