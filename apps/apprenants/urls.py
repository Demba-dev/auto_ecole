# apps/apprenants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_apprenants, name='liste_apprenants'),
    path('ajouter/', views.ajouter_apprenant, name='ajouter_apprenant'),
    path('<int:pk>/', views.detail_apprenant, name='detail_apprenant'),
    path('<int:pk>/modifier/', views.modifier_apprenant, name='modifier_apprenant'),
    path('<int:pk>/supprimer/', views.supprimer_apprenant, name='supprimer_apprenant'),
    path('<int:pk>/planning/', views.planning_apprenant, name='planning_apprenant'),
    path('<int:pk>/dossier/creer/', views.creer_dossier, name='creer_dossier'),
    path('<int:pk>/dossier/modifier/', views.modifier_dossier, name='modifier_dossier'),
    path('<int:pk>/progression/ajouter/', views.ajouter_progression, name='ajouter_progression'),
    path('exporter/', views.exporter_apprenants, name='exporter_apprenants'),
]
