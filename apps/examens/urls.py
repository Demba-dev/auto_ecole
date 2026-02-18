from django.urls import path
from . import views

app_name = 'examens'

urlpatterns = [
    path('', views.examens_hub, name='hub'),

    path('activites/', views.activites, name='activites'),
    path('planning/', views.planning, name='planning'),
    path('statistiques/', views.statistiques, name='statistiques'),
    path('export/', views.examen_export, name='examen_export'),
    
    path('liste/', views.examen_list, name='examen_list'),
    path('creer/', views.examen_create, name='examen_create'),
    path('<int:pk>/modifier/', views.examen_update, name='examen_update'),
    path('<int:pk>/valider/', views.examen_validate, name='examen_validate'),
    path('<int:pk>/paiement/', views.examen_paiement, name='examen_paiement'),
    path('<int:pk>/imprimer/', views.examen_print, name='examen_print'),
    path('<int:pk>/', views.examen_detail, name='examen_detail'),
    path('<int:pk>/supprimer/', views.examen_delete, name='examen_delete'),
]