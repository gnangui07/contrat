from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    # Contrats
    path('', views.contract_list, name='list'),
    path('<int:pk>/', views.contract_detail, name='detail'),
    path('create/', views.contract_create, name='create'),
    path('<int:pk>/edit/', views.contract_edit, name='edit'),
    path('<int:pk>/validate/', views.contract_validate, name='validate'),
    path('<int:pk>/reject/', views.contract_reject, name='reject'),
]
