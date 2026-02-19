from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    path('backup/create/', views.create_backup, name='create_backup'),
    path('backup/restore/<str:filename>/', views.restore_backup, name='restore_backup'),
]
