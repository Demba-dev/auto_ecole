from django import forms
from .models import Seance
from django.utils import timezone
from apps.accounts.models import User


class SeanceForm(forms.ModelForm):

    class Meta:
        model = Seance
        fields = [
            'type_seance',
            'date',
            'heure_debut',
            'duree_minutes',
            'apprenant',
            'moniteur',
            'vehicule',
            'statut',
            'compte_rendu'
        ]

        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'heure_debut': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
            'type_seance': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'apprenant': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'moniteur': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'vehicule': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'statut': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'duree_minutes': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 15, 'step': 15}
            ),
            'compte_rendu': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }

    # ✅ Filtrer uniquement les moniteurs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optionnel : rendre véhicule obligatoire seulement si conduite
        self.fields['vehicule'].required = False

    # ✅ Validation propre (au lieu de ValueError dans save)
    def clean(self):
        cleaned_data = super().clean()
        type_seance = cleaned_data.get("type_seance")
        vehicule = cleaned_data.get("vehicule")

        # Si c'est une séance de conduite, véhicule obligatoire
        if type_seance == "CONDUITE" and not vehicule:
            self.add_error('vehicule', "Un véhicule est obligatoire pour une leçon de conduite.")

        return cleaned_data
    

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date and date < timezone.now().date():
            raise forms.ValidationError("Impossible de planifier dans le passé.")
        return date
