from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # On autorise si c'est un ADMIN ou un superutilisateur Django
        if request.user.role == 'ADMIN' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
