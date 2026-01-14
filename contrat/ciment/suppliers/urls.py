from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='list'),
    path('create/', views.supplier_create, name='create'),
    path('<int:pk>/', views.supplier_detail, name='detail'),
    path('<int:pk>/edit/', views.supplier_edit, name='edit'),
    path('<int:pk>/delete/', views.supplier_delete, name='delete'),
    # Nouvelles URLs pour l'autocomplétion
    path('api/banques/autocomplete/', views.autocomplete_banques, name='autocomplete_banques'),
    path('api/banques/<int:banque_id>/', views.get_banque_details, name='get_banque_details'),
    # URLs existantes pour les emails
    path('<int:pk>/eval-summary/', views.get_eval_summary, name='get_eval_summary'),
    path('<int:pk>/send-mail/', views.send_supplier_mail, name='send_supplier_mail'),
]
