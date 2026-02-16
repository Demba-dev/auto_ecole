from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError

class AdminAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.role != 'ADMIN':
            raise ValidationError(
                "Accès restreint aux administrateurs uniquement.",
                code="closed_access",
            )
