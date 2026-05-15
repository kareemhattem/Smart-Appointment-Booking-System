from django.urls import path
from . import views

app_name = 'providers'

urlpatterns = [
    path('', views.provider_list, name='list'),
    path('<int:pk>/', views.provider_detail, name='detail'),
    path('manage/profile/', views.manage_profile, name='manage_profile'),
    path('manage/slots/', views.manage_slots, name='manage_slots'),
    path('manage/slots/<int:pk>/delete/', views.delete_slot, name='delete_slot'),
]
