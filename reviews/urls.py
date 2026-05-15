from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('appointment/<int:appointment_id>/review/', views.leave_review, name='leave_review'),
    path('provider/<int:provider_id>/', views.provider_reviews, name='provider_reviews'),
]
