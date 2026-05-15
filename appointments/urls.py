from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.my_appointments, name='my_appointments'),
    path('book/<int:provider_id>/', views.book_appointment, name='book'),
    path('<int:pk>/', views.appointment_detail, name='detail'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
    path('<int:pk>/confirm/', views.confirm_appointment, name='confirm'),
    path('<int:pk>/reject/', views.reject_appointment, name='reject'),
    path('<int:pk>/complete/', views.complete_appointment, name='complete'),
]
