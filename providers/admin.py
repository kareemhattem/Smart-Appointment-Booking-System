from django.contrib import admin
from .models import Category, ProviderProfile, AvailabilitySlot


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'title', 'experience_years', 'consultation_fee', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['user__username', 'user__first_name', 'specialization']


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['provider', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
