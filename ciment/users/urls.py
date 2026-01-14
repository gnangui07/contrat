from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Accueil
    path('', views.home_view, name='home'),
    
    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Activation
    path('activate/<str:token>/', views.activate_account, name='activate'),
    path('confirm/<str:token>/', views.confirm_password, name='confirm_password'),
    

]
