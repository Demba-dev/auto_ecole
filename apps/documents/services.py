from .models import Document
from django.core.files.base import ContentFile
from django.utils import timezone

# -------------------------------
# Upload de document
# -------------------------------
def upload_document(apprenant, fichier, type_document):
    """
    Crée un document pour un apprenant.
    """
    doc = Document.objects.create(
        apprenant=apprenant,
        fichier=fichier,
        type_document=type_document,
        date_upload=timezone.now(),
        est_valide=False
    )
    return doc


# -------------------------------
# Valider un document
# -------------------------------
def valider_document(document_id):
    """
    Marque un document comme validé.
    """
    doc = Document.objects.get(pk=document_id)
    doc.est_valide = True
    doc.save()
    return doc


# -------------------------------
# Rejeter un document avec commentaire
# -------------------------------
def rejeter_document(document_id, commentaire):
    doc = Document.objects.get(pk=document_id)
    doc.est_valide = False
    doc.commentaire = commentaire
    doc.save()
    return doc


# -------------------------------
# Lister documents par type
# -------------------------------
def documents_par_type(apprenant, type_document):
    """
    Retourne tous les documents d’un type pour un apprenant.
    """
    return Document.objects.filter(apprenant=apprenant, type_document=type_document)


# -------------------------------
# Suppression sécurisée
# -------------------------------
def supprimer_document(document_id):
    doc = Document.objects.get(pk=document_id)
    doc.fichier.delete(save=False)  # supprime le fichier physiquement
    doc.delete()                     # supprime la ligne en DB
