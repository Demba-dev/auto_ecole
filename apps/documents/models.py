from django.db import models

class Document(models.Model):
    TYPE_CHOICES = [
        ('CNI', 'Carte d’identité'),
        ('PERMIS', 'Permis'),
        ('PHOTO', 'Photo'),
        ('CONTRAT', 'Contrat signé'),
        ('AUTRE', 'Autre'),
    ]

    apprenant = models.ForeignKey(
        'apprenants.Apprenant',
        on_delete=models.CASCADE,
        related_name='documents'
    )

    type_document = models.CharField(max_length=20, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    date_upload = models.DateTimeField(auto_now_add=True)

    est_valide = models.BooleanField(default=False)
    commentaire = models.TextField(blank=True)

    def __str__(self):
        return f"{self.apprenant} - {self.get_type_document_display()}"
