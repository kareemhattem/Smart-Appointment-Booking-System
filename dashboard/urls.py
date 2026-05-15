from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.home, name='home'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/users/', views.admin_users, name='admin_users'),
    path('dashboard/admin/users/<int:pk>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('dashboard/admin/appointments/', views.admin_appointments, name='admin_appointments'),
]
