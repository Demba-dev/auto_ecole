from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from apps.accounts.decorators import admin_required
from .models import Document
from .forms import DocumentUploadForm, DocumentValidationForm, DocumentFilterForm

# -------------------------------
# Liste des documents avec filtre
# -------------------------------
@admin_required
def document_list(request):
    documents = Document.objects.select_related('apprenant').order_by('-date_upload')
    documents_valides = documents.filter(est_valide=True).count()
    apprenants_avec_docs = documents.values_list('apprenant__id', flat=True).distinct().count()
    documents_non_valides = documents.filter(est_valide=False).count()
    
    # Filtrage
    filter_form = DocumentFilterForm(request.GET or None)
    if filter_form.is_valid():
        type_doc = filter_form.cleaned_data.get('type_document')
        est_valide = filter_form.cleaned_data.get('est_valide')
        nom = filter_form.cleaned_data.get('apprenant_nom')

        if type_doc:
            documents = documents.filter(type_document=type_doc)
        if est_valide in ['0', '1']:
            documents = documents.filter(est_valide=bool(int(est_valide)))
        if nom:
            documents = documents.filter(apprenant__nom__icontains=nom)

    context = {
        'documents': documents,
        'filter_form': filter_form,
        'documents_valides': documents_valides,
        'apprenants_avec_docs': apprenants_avec_docs,
        'documents_non_valides': documents_non_valides,
    }
    return render(request, 'documents/document_list.html', context)


# -------------------------------
# Upload / création de document
# -------------------------------
@admin_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            # Use the apprenant chosen in the form (the form provides a proper Apprenant instance)
            doc.save()
            messages.success(request, "Document uploadé avec succès !")
            return redirect(reverse('documents:document_list'))
        else:
            messages.error(request, "Erreur lors de l'upload, veuillez vérifier le formulaire.")
    else:
        form = DocumentUploadForm()

    return render(request, 'documents/document_upload.html', {'form': form})


@admin_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, "Document mis à jour avec succès !")
            return redirect(reverse('documents:document_list'))
        else:
            messages.error(request, "Erreur lors de la mise à jour, veuillez vérifier le formulaire.")
    else:
        form = DocumentUploadForm(instance=doc)

    return render(request, 'documents/document_upload.html', {'form': form, 'document': doc})

@admin_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        doc.fichier.delete(save=False)  # supprime le fichier physiquement
        doc.delete()                     # supprime la ligne en DB
        messages.success(request, "Document supprimé avec succès !")
        return redirect(reverse('documents:document_list'))
    return render(request, 'documents/document_confirm_delete.html', {'document': doc})


# -------------------------------
# Validation / rejet d’un document
# -------------------------------
@admin_required
def document_validate(request, pk):
    doc = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        form = DocumentValidationForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, "Document mis à jour avec succès !")
            return redirect(reverse('documents:document_list'))
        else:
            messages.error(request, "Erreur lors de la validation, veuillez vérifier le formulaire.")
    else:
        form = DocumentValidationForm(instance=doc)

    return render(request, 'documents/document_validate.html', {'form': form, 'document': doc})


# -------------------------------
# Détails d’un document
# -------------------------------
@admin_required
def document_detail(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return render(request, 'documents/document_detail.html', {'document': doc})
