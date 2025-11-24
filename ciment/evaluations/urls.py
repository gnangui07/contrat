from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    # Evaluations Vendor
    path('', views.evaluation_list, name='list'),
    path('<int:pk>/', views.evaluation_detail, name='detail'),
    path('create/', views.evaluation_create, name='create'),
    path('<int:pk>/edit/', views.evaluation_edit, name='edit'),
    path('<int:pk>/delete/', views.evaluation_delete, name='delete'),
    
    # Evaluations Acheteur
    path('buyer/', views.buyer_evaluation_list, name='buyer_list'),
    path('buyer/<int:pk>/', views.buyer_evaluation_detail, name='buyer_detail'),
    path('buyer/create/', views.buyer_evaluation_create, name='buyer_create'),
    path('buyer/<int:pk>/edit/', views.buyer_evaluation_edit, name='buyer_edit'),
    path('buyer/<int:pk>/delete/', views.buyer_evaluation_delete, name='buyer_delete'),
    
    # Evaluations par fournisseur
    path('supplier/<int:supplier_id>/', views.supplier_evaluations, name='supplier_evaluations'),
    path('supplier/<int:supplier_id>/buyer/', views.supplier_buyer_evaluations, name='supplier_buyer_evaluations'),

    # Rankings (avec notes pondérées)
    path('ranking/', views.ranking_overview, name='ranking_overview'),
    path('ranking/export.xlsx', views.export_ranking_xlsx, name='export_ranking_xlsx'),
    path('ranking/export/top.csv', views.export_ranking_top_csv, name='export_ranking_top_csv'),
    path('ranking/export/bottom.csv', views.export_ranking_bottom_csv, name='export_ranking_bottom_csv'),
    path('ranking/export/supplier.csv', views.export_supplier_ranking_csv, name='export_supplier_ranking_csv'),
]
