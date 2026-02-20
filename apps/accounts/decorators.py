from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
        # Autoriser si rôle ADMIN ou superutilisateur
        if getattr(request.user, 'role', None) == 'ADMIN' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied

    return _wrapped_view
