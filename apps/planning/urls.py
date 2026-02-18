from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.planning_hub, name='planning_hub'),
    path('<str:section>/', views.planning_hub, name='planning_hub_section'),

    path('seance/create/', views.seance_create, name='seance_create'),
    path('seance/<int:pk>/edit/', views.seance_update, name='seance_update'),
    path('seance/<int:pk>/delete/', views.seance_delete, name='seance_delete'),
]
