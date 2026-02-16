from django.urls import path
from . import views

app_name = 'personnel'

urlpatterns = [
    # Hub général avec sections
    path('', views.personnel_hub, name='hub'),
    path('', views.personnel_hub, name='employe_list'), # Alias
    path('moniteurs/', views.personnel_hub, {'section': 'moniteur'}, name='moniteur_list'), # Alias
    path('affectations/', views.personnel_hub, {'section': 'affectation'}, name='affectation_list'), # Alias
    path('disponibilites/', views.personnel_hub, {'section': 'disponibilite'}, name='disponibilite_list'), # Alias
    path('<str:section>/', views.personnel_hub, name='hub_section'),

    # CRUD Employés
    path('employe/create/', views.employe_create, name='employe_create'),
    path('employe/<int:pk>/edit/', views.employe_update, name='employe_update'),
    path('employe/<int:pk>/delete/', views.employe_delete, name='employe_delete'),
    path('employe/<int:pk>/', views.employe_detail, name='employe_detail'),

    # CRUD Moniteurs
    path('moniteur/create/', views.moniteur_create, name='moniteur_create'),
    path('moniteur/<int:pk>/edit/', views.moniteur_update, name='moniteur_update'),
    path('moniteur/<int:pk>/delete/', views.moniteur_delete, name='moniteur_delete'),

    # CRUD Affectations
    path('affectation/create/', views.affectation_create, name='affectation_create'),
    path('affectation/<int:pk>/edit/', views.affectation_update, name='affectation_update'),
    path('affectation/<int:pk>/delete/', views.affectation_delete, name='affectation_delete'),

    # CRUD Disponibilités
    path('disponibilite/create/', views.disponibilite_create, name='disponibilite_create'),
    path('disponibilite/<int:pk>/edit/', views.disponibilite_update, name='disponibilite_update'),
    path('disponibilite/<int:pk>/delete/', views.disponibilite_delete, name='disponibilite_delete'),
]
