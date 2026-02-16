from django import forms
from .models import Employe, MoniteurProfile, AffectationMoniteur, DisponibiliteMoniteur

# -------------------------
# Formulaire Employe
# -------------------------
class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['nom', 'prenom', 'email', 'type_employe', 'telephone', 'date_embauche', 'actif']
        widgets = {
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On ne gère plus le queryset user car il est caché du formulaire


# -------------------------
# Formulaire MoniteurProfile
# -------------------------
class MoniteurProfileForm(forms.ModelForm):
    class Meta:
        model = MoniteurProfile
        fields = ['employe', 'numero_agrement', 'specialites', 'taux_horaire']
        widgets = {
            'specialites': forms.CheckboxSelectMultiple,
        }


# -------------------------
# Formulaire AffectationMoniteur
# -------------------------
class AffectationMoniteurForm(forms.ModelForm):
    class Meta:
        model = AffectationMoniteur
        fields = ['apprenant', 'moniteur', 'date_debut', 'actif']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
        }


# -------------------------
# Formulaire DisponibiliteMoniteur
# -------------------------
class DisponibiliteMoniteurForm(forms.ModelForm):
    class Meta:
        model = DisponibiliteMoniteur
        fields = ['moniteur', 'jour_semaine', 'heure_debut', 'heure_fin', 'actif']
        widgets = {
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        debut = cleaned_data.get("heure_debut")
        fin = cleaned_data.get("heure_fin")
        if debut and fin and fin <= debut:
            raise forms.ValidationError("L'heure de fin doit être après l'heure de début.")
        return cleaned_data
