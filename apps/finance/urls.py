from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.finance_hub, name='hub'),
    path('<str:section>/', views.finance_hub, name='hub_section'),

    # CRUD
    path('tarif/create/', views.tarif_create, name='tarif_create'),
    path('tarif/<int:pk>/edit/', views.tarif_update, name='tarif_update'),
    path('tarif/<int:pk>/delete/', views.tarif_delete, name='tarif_delete'),

    path('contrat/create/', views.contrat_create, name='contrat_create'),
    path('contrat/<int:pk>/edit/', views.contrat_update, name='contrat_update'),
    path('contrat/<int:pk>/delete/', views.contrat_delete, name='contrat_delete'),

    path('paiement/create/', views.paiement_create, name='paiement_create'),
    path('paiement/<int:pk>/', views.paiement_detail, name='paiement_detail'),
    path('paiement/<int:pk>/delete/', views.paiement_delete, name='paiement_delete'),

    # API
    path('api/contrat/<int:pk>/info/', views.get_contrat_info, name='api_contrat_info'),
]
