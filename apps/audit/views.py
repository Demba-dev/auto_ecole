import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import AuditLog

@user_passes_test(lambda u: u.is_superuser)
def audit_log_list(request):
    logs = AuditLog.objects.select_related('user', 'content_type').all()[:100]
    return render(request, 'audit/log_list.html', {'logs': logs})

@user_passes_test(lambda u: u.is_superuser)
def audit_export(request):
    """Exporte les logs d'audit en format CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Utilisateur', 'Action', 'Objet', 'IP', 'Détails'])
    
    logs = AuditLog.objects.select_related('user').all().order_by('-timestamp')
    
    for log in logs:
        writer.writerow([
            log.timestamp.strftime("%d/%m/%Y %H:%M"),
            log.user.username if log.user else "N/A",
            log.get_action_display(),
            log.object_repr,
            log.ip_address or "N/A",
            log.changes or ""
        ])
        
    return response
