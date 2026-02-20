from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError
from .models import User

class AdminAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        # Autoriser si le rôle est ADMIN OU si c'est un superutilisateur
        if user.role != 'ADMIN' and not user.is_superuser:
            raise ValidationError(
                "Accès restreint aux administrateurs uniquement.",
                code="closed_access",
            )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
