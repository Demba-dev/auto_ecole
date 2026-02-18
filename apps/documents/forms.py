from django import forms
from .models import Document
from apps.apprenants.models import Apprenant

# -------------------------------
# Formulaire d'upload / création
# -------------------------------
class DocumentUploadForm(forms.ModelForm):
    apprenant = forms.ModelChoiceField(
        queryset=Apprenant.objects.all(),
        label="Apprenant"
    )
    class Meta:
        model = Document
        fields = ['apprenant', 'fichier', 'type_document','est_valide', 'commentaire']
        widgets = {
            'apprenant': forms.Select(attrs={'class': 'form-select'}),
            'type_document': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'est_valide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'fichier': "Fichier à télécharger",
            'type_document': "Type de document",
        }

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            # Limite de taille : 10 Mo
            max_size = 10 * 1024 * 1024
            if fichier.size > max_size:
                raise forms.ValidationError("Le fichier est trop volumineux (max 10 Mo).")
            
            # Vérification type MIME (optionnel)
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
            if hasattr(fichier, 'content_type') and fichier.content_type not in allowed_types:
                raise forms.ValidationError("Format non autorisé. Autorisé : PDF, JPG, PNG.")
        return fichier


# -------------------------------
# Formulaire de validation / rejet
# -------------------------------
class DocumentValidationForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['est_valide', 'commentaire']
        widgets = {
            'est_valide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'est_valide': "Valider le document",
            'commentaire': "Commentaire (si rejeté)",
        }

    def clean(self):
        cleaned_data = super().clean()
        est_valide = cleaned_data.get('est_valide')
        commentaire = cleaned_data.get('commentaire')

        # Si rejeté, commentaire obligatoire
        if est_valide is False and not commentaire:
            self.add_error('commentaire', "Vous devez fournir un commentaire si vous rejetez le document.")
        return cleaned_data


# -------------------------------
# Filtrage / recherche documents (optionnel)
# -------------------------------
class DocumentFilterForm(forms.Form):
    type_document = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Document.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    est_valide = forms.ChoiceField(
        choices=[('', 'Tous'), ('1', 'Validé'), ('0', 'Non validé')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    apprenant_nom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l’apprenant'})
    )
