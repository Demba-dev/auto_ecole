from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .utils import log_action

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_action(user=user, action='LOGIN', request=request)

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        log_action(user=user, action='LOGOUT', request=request)

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    # On log la tentative infructueuse (attention à ne pas logger le mot de passe !)
    username = credentials.get('username', 'Inconnu')
    log_action(
        user=None, 
        action='LOGIN', 
        object_repr=f"Échec de connexion pour : {username}",
        request=request
    )
