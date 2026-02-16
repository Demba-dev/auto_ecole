from django.urls import path
from . import views

app_name = 'vehicules'

urlpatterns = [
    path('', views.vehicules_hub, name='vehicules_hub'),
    path('<str:section>/', views.vehicules_hub, name='vehicules_hub_section'),
    
    # CRUD Véhicule
    path('vehicules/', views.vehicule_list, name='vehicule_list'),
    path('vehicules/create/', views.vehicule_create, name='vehicule_create'),
    path('vehicules/<int:pk>/edit/', views.vehicule_update, name='vehicule_update'),
    path('vehicules/<int:pk>/delete/', views.vehicule_delete, name='vehicule_delete'),

    # CRUD Maintenance
    path('maintenances/', views.maintenance_list, name='maintenance_list'),
    path('maintenances/create/', views.maintenance_create, name='maintenance_create'),
    path('maintenances/<int:pk>/edit/', views.maintenance_update, name='maintenance_update'),
    path('maintenances/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
]