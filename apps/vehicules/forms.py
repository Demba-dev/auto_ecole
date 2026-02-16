from django import forms
from .models import Vehicule, Maintenance

class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = [
            'immatriculation',
            'marque',
            'modele',
            'type_boite',
            'energie',
            'kilometrage_initial',
            'date_mise_circulation',
            'statut'
        ]
        widgets = {
            'immatriculation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: AB-123-CD'}),
            'marque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Toyota'}),
            'modele': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Hilux'}),
            'kilometrage_initial': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'date_mise_circulation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_boite': forms.Select(attrs={'class': 'form-select'}),
            'energie': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'vehicule',
            'date',
            'type_maintenance',
            'kilometrage',
            'prestataire',
            'montant',
            'prochaine_echeance'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'prochaine_echeance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
