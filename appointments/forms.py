from django import forms
from django.utils import timezone
from .models import Appointment


class BookAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'start_time', 'end_time', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for appointment...'}),
        }

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('appointment_date')
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')

        if date and date < timezone.now().date():
            raise forms.ValidationError('Appointment date cannot be in the past.')

        if start and end and start >= end:
            raise forms.ValidationError('End time must be after start time.')

        return cleaned


class AppointmentNotesForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
