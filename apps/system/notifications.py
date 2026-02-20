from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def notify_apprenant_seance(seance):
    """Notification d'une nouvelle séance créée"""
    if not seance.apprenant.email:
        return
        
    subject = f"Nouvelle séance de {seance.get_type_seance_display()} confirmée"
    
    # On pourrait utiliser un template HTML ici
    message = f"Bonjour {seance.apprenant.prenom},\n\n"
    message += f"Votre séance de {seance.get_type_seance_display()} a été programmée :\n"
    message += f"📅 Date : {seance.date.strftime('%d/%m/%Y')}\n"
    message += f"⏰ Heure : {seance.heure_debut.strftime('%H:%M')}\n"
    message += f"🚗 Véhicule : {seance.vehicule if seance.vehicule else 'À confirmer'}\n"
    message += f"👨‍🏫 Moniteur : {seance.moniteur}\n\n"
    message += "À bientôt !\nL'équipe KALANSSO"
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [seance.apprenant.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur d'envoi d'email : {e}")
        return False
