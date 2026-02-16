from django import forms
from .models import Apprenant, DossierApprenant, ProgressionConduite

class ApprenantForm(forms.ModelForm):
    class Meta:
        model = Apprenant
        exclude = ['user']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class DossierForm(forms.ModelForm):
    class Meta:
        model = DossierApprenant
        fields = ['piece_identite', 'photo', 'certificat_medical']

class ProgressionForm(forms.ModelForm):
    class Meta:
        model = ProgressionConduite
        fields = ['heures_achetees', 'heures_effectuees']
