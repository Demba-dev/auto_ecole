from .models import SystemSettings

def system_settings(request):
    """
    Rend les paramètres du système accessibles dans tous les templates.
    """
    settings, created = SystemSettings.objects.get_or_create(id=1)
    return {
        'system_settings': settings
    }
