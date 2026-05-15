from django.db import models
from accounts.models import User


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_appointments')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-start_time']

    def __str__(self):
        return f'{self.patient.username} → {self.provider.username} on {self.appointment_date} at {self.start_time}'

    def is_cancellable(self):
        return self.status in ['pending', 'confirmed']

    def get_status_badge(self):
        badges = {
            'pending': 'warning',
            'confirmed': 'success',
            'cancelled': 'secondary',
            'completed': 'primary',
            'rejected': 'danger',
        }
        return badges.get(self.status, 'secondary')
