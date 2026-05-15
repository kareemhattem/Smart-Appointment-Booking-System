from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'provider', 'appointment_date', 'start_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_date']
    search_fields = ['patient__username', 'provider__username']
    ordering = ['-appointment_date']
    readonly_fields = ['created_at', 'updated_at']
