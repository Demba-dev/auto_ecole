from django import forms
from .models import Examen
from apps.personnel.models import Employe
from apps.planning.models import Seance
from apps.vehicules.models import Vehicule

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = [
            'seance',
            'apprenant',
            'moniteur',
            'vehicule',
            'type_examen',
            'date',
            'heure_debut',
            'duree_minutes',
            'result',
            'notes',
            'est_paye',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duree_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seance'].queryset = Seance.objects.filter(type_seance='EXAMEN').exclude(examen__isnull=False)
        self.fields['moniteur'].queryset = Employe.objects.filter(type_employe='MONITEUR')
        self.fields['vehicule'].required = False

    def clean(self):
        cleaned_data = super().clean()
        seance = cleaned_data.get("seance")

        if seance:
            cleaned_data['apprenant'] = seance.apprenant
            cleaned_data['moniteur'] = seance.moniteur
            if cleaned_data.get("type_examen") == "CONDUITE":
                cleaned_data['vehicule'] = seance.vehicule
            else:
                cleaned_data['vehicule'] = None

        type_examen = cleaned_data.get("type_examen")
        vehicule = cleaned_data.get("vehicule")
        if type_examen == "CONDUITE" and not vehicule:
            self.add_error('vehicule', "Un véhicule est obligatoire pour un examen pratique.")

        return cleaned_data

class ExamenResultForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['result', 'notes']
        widgets = {
            'result': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Observations facultatives...'}),
        }

