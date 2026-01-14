from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Reports
    path('', views.reports_list, name='list'),
    path('export/contracts/', views.export_contracts_csv, name='export_contracts_csv'),
    path('export/suppliers/', views.export_suppliers_csv, name='export_suppliers_csv'),
    path('export/evaluations/', views.export_evaluations_csv, name='export_evaluations_csv'),
]
