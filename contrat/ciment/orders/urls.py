from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.purchase_order_list, name="purchase_order_list"),
    path("<str:number>/", views.purchase_order_detail, name="purchase_order_detail"),
]
