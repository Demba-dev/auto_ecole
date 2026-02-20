from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

def log_action(user, action, instance=None, object_repr=None, changes=None, request=None):
    """
    Enregistre une action d'audit dans la base de données.
    
    :param user: L'utilisateur qui a effectué l'action
    :param action: Le type d'action ('CREATE', 'UPDATE', etc.)
    :param instance: L'objet concerné par l'action (optionnel)
    :param object_repr: Représentation textuelle si instance est absent (optionnel)
    :param changes: Un dictionnaire représentant les changements effectués (optionnel)
    :param request: L'objet request pour extraire l'IP et le UserAgent (optionnel)
    """
    
    audit_data = {
        'user': user,
        'action': action,
        'changes': changes,
    }
    
    if instance:
        audit_data['content_type'] = ContentType.objects.get_for_model(instance)
        audit_data['object_id'] = instance.pk
        audit_data['object_repr'] = str(instance)
    elif object_repr:
        audit_data['object_repr'] = object_repr
    else:
        audit_data['object_repr'] = "N/A"
        
    if request:
        # Extraire l'IP réelle même derrière un proxy (comme Nginx)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            audit_data['ip_address'] = x_forwarded_for.split(',')[0]
        else:
            audit_data['ip_address'] = request.META.get('REMOTE_ADDR')
            
        audit_data['user_agent'] = request.META.get('HTTP_USER_AGENT')
        
    return AuditLog.objects.create(**audit_data)
