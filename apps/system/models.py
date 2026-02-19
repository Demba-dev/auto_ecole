from django.db import models

class SystemSettings(models.Model):
    app_name = models.CharField(max_length=100, default='KALANSSO ERP')
    app_logo = models.ImageField(upload_to='system/logos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Paramètres de sauvegarde
    auto_backup = models.BooleanField(default=False)
    backup_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Quotidienne'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuelle'),
    ], default='daily')
    backup_time = models.TimeField(default='02:00')
    last_backup = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Paramètres du système"
        verbose_name_plural = "Paramètres du système"

    def __str__(self):
        return self.app_name
