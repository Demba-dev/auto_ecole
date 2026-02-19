import os
import shutil
from django.conf import settings
from datetime import datetime

def backup_database():
    """
    Crée une copie de la base de données SQLite actuelle.
    """
    db_path = settings.DATABASES['default']['NAME']
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'db_backup_{timestamp}.sqlite3')
    
    shutil.copy2(db_path, backup_path)
    return backup_path

def get_backups():
    """
    Liste tous les fichiers de sauvegarde disponibles.
    """
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        return []
    
    backups = []
    for filename in os.listdir(backup_dir):
        if filename.endswith('.sqlite3'):
            path = os.path.join(backup_dir, filename)
            backups.append({
                'filename': filename,
                'size': os.path.getsize(path),
                'date': datetime.fromtimestamp(os.path.getmtime(path))
            })
    
    # Trier par date décroissante
    backups.sort(key=lambda x: x['date'], reverse=True)
    return backups

def restore_database(backup_filename):
    """
    Restaure la base de données à partir d'un fichier de sauvegarde.
    """
    backup_path = os.path.join(settings.BASE_DIR, 'backups', backup_filename)
    db_path = settings.DATABASES['default']['NAME']
    
    if os.path.exists(backup_path):
        # On fait une sauvegarde de sécurité de l'actuelle avant d'écraser
        backup_database()
        shutil.copy2(backup_path, db_path)
        return True
    return False
