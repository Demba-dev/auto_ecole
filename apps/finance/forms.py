from django import forms
from django.db.models import Sum
from .models import Tarif, Contrat, Paiement


# ==========================
# FORMULAIRE TARIF
# ==========================
class TarifForm(forms.ModelForm):
    class Meta:
        model = Tarif
        fields = [
            "type_permis",
            "libelle",
            "montant",
            "heures_inclues",
            "description",
            "actif",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


# ==========================
# FORMULAIRE CONTRAT
# ==========================
class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = [
            "apprenant",
            "tarif",
            "montant_total",
            "heures_inclues",
            "heures_effectuees",
            "date_debut",
            "date_fin",
            "actif",
        ]
        widgets = {
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si un tarif est choisi, pré-remplir montant et heures
        if "tarif" in self.data:
            try:
                tarif_id = int(self.data.get("tarif"))
                tarif = Tarif.objects.get(id=tarif_id)
                self.fields["montant_total"].initial = tarif.montant
                self.fields["heures_inclues"].initial = tarif.heures_inclues
            except (ValueError, TypeError, Tarif.DoesNotExist):
                pass

    def clean(self):
        cleaned_data = super().clean()

        montant_total = cleaned_data.get("montant_total")
        heures_inclues = cleaned_data.get("heures_inclues")
        heures_effectuees = cleaned_data.get("heures_effectuees")

        if montant_total and montant_total <= 0:
            raise forms.ValidationError("Le montant total doit être supérieur à 0.")

        if heures_effectuees and heures_inclues:
            if heures_effectuees > heures_inclues:
                raise forms.ValidationError(
                    "Les heures effectuées ne peuvent pas dépasser les heures incluses."
                )

        return cleaned_data


# ==========================
# FORMULAIRE PAIEMENT
# ==========================
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = [
            "contrat",
            "montant",
            "date_paiement",
            "mode",
            "reference",
        ]
        widgets = {
            "date_paiement": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "reference": forms.TextInput(attrs={"readonly": "readonly", "placeholder": "Générée automatiquement"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        contrat = cleaned_data.get("contrat")
        montant = cleaned_data.get("montant")

        if montant and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")

        if contrat and montant:
            total_paye = contrat.paiements.aggregate(
                total=Sum("montant")
            )["total"] or 0

            if total_paye + montant > contrat.montant_total:
                raise forms.ValidationError(
                    "Ce paiement dépasse le montant total du contrat."
                )

        return cleaned_data
