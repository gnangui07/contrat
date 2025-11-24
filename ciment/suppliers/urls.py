from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    # Suppliers
    path('', views.supplier_list, name='list'),
    path('<int:pk>/', views.supplier_detail, name='detail'),
    path('create/', views.supplier_create, name='create'),
    path('<int:pk>/edit/', views.supplier_edit, name='edit'),
    path('<int:pk>/delete/', views.supplier_delete, name='delete'),
    path('<int:pk>/send_mail/', views.send_supplier_mail, name='send_mail'),
    path('<int:pk>/get_eval_summary/', views.get_eval_summary, name='get_eval_summary'),
]
