from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Appointment
from .forms import BookAppointmentForm, AppointmentNotesForm
from accounts.models import User
from notifications.models import Notification


def check_overlap(provider, date, start_time, end_time, exclude_id=None):
    qs = Appointment.objects.filter(
        provider=provider,
        appointment_date=date,
        status__in=['pending', 'confirmed'],
    ).filter(
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


@login_required
def book_appointment(request, provider_id):
    provider = get_object_or_404(User, id=provider_id, role='provider')

    if request.user == provider:
        messages.error(request, 'You cannot book an appointment with yourself.')
        return redirect('providers:list')

    if request.method == 'POST':
        form = BookAppointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['appointment_date']
            start = form.cleaned_data['start_time']
            end = form.cleaned_data['end_time']

            if check_overlap(provider, date, start, end):
                messages.error(request, 'This time slot is already booked. Please choose a different time.')
                return render(request, 'appointments/book.html', {'form': form, 'provider': provider})

            existing = Appointment.objects.filter(
                patient=request.user,
                provider=provider,
                appointment_date=date,
                status__in=['pending', 'confirmed'],
            ).exists()

            if existing:
                messages.error(request, 'You already have a pending or confirmed appointment with this provider on that date.')
                return render(request, 'appointments/book.html', {'form': form, 'provider': provider})

            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.provider = provider
            appointment.save()

            Notification.send(
                recipient=provider,
                title='New Appointment Request',
                message=f'{request.user.get_full_name() or request.user.username} has requested an appointment on {date} at {start}.',
                notification_type='appointment_booked',
            )
            Notification.send(
                recipient=request.user,
                title='Appointment Submitted',
                message=f'Your appointment with {provider.get_full_name() or provider.username} on {date} at {start} is pending confirmation.',
                notification_type='appointment_booked',
            )

            messages.success(request, 'Appointment booked successfully! Waiting for provider confirmation.')
            return redirect('appointments:my_appointments')
    else:
        form = BookAppointmentForm()

    return render(request, 'appointments/book.html', {'form': form, 'provider': provider})


@login_required
def my_appointments(request):
    if request.user.is_provider():
        appointments = Appointment.objects.filter(provider=request.user).select_related('patient')
    else:
        appointments = Appointment.objects.filter(patient=request.user).select_related('provider')

    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
    })


@login_required
def appointment_detail(request, pk):
    if request.user.is_provider():
        appointment = get_object_or_404(Appointment, pk=pk, provider=request.user)
    elif request.user.is_admin():
        appointment = get_object_or_404(Appointment, pk=pk)
    else:
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    return render(request, 'appointments/detail.html', {'appointment': appointment})


@login_required
def cancel_appointment(request, pk):
    if request.user.is_provider():
        appointment = get_object_or_404(Appointment, pk=pk, provider=request.user)
    else:
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    if not appointment.is_cancellable():
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('appointments:my_appointments')

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()

        other_party = appointment.provider if request.user == appointment.patient else appointment.patient
        Notification.send(
            recipient=other_party,
            title='Appointment Cancelled',
            message=f'The appointment on {appointment.appointment_date} at {appointment.start_time} has been cancelled.',
            notification_type='appointment_cancelled',
        )

        messages.success(request, 'Appointment cancelled.')
        return redirect('appointments:my_appointments')

    return render(request, 'appointments/cancel_confirm.html', {'appointment': appointment})


@login_required
def confirm_appointment(request, pk):
    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    appointment = get_object_or_404(Appointment, pk=pk, provider=request.user, status='pending')

    if request.method == 'POST':
        appointment.status = 'confirmed'
        appointment.save()

        Notification.send(
            recipient=appointment.patient,
            title='Appointment Confirmed',
            message=f'Your appointment on {appointment.appointment_date} at {appointment.start_time} has been confirmed.',
            notification_type='appointment_confirmed',
        )

        messages.success(request, 'Appointment confirmed.')
        next_url = request.POST.get('next', 'appointments:my_appointments')
        if next_url == 'dashboard':
            return redirect('dashboard:home')
        return redirect('appointments:my_appointments')

    return render(request, 'appointments/confirm.html', {'appointment': appointment})


@login_required
def reject_appointment(request, pk):
    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    appointment = get_object_or_404(Appointment, pk=pk, provider=request.user, status='pending')

    if request.method == 'POST':
        appointment.status = 'rejected'
        appointment.save()

        Notification.send(
            recipient=appointment.patient,
            title='Appointment Rejected',
            message=f'Your appointment request on {appointment.appointment_date} at {appointment.start_time} was not accepted.',
            notification_type='appointment_rejected',
        )

        messages.warning(request, 'Appointment rejected.')
        next_url = request.POST.get('next', '')
        if next_url == 'dashboard':
            return redirect('dashboard:home')
        return redirect('appointments:my_appointments')

    return render(request, 'appointments/reject.html', {'appointment': appointment})


@login_required
def complete_appointment(request, pk):
    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    appointment = get_object_or_404(Appointment, pk=pk, provider=request.user, status='confirmed')

    if request.method == 'POST':
        appointment.status = 'completed'
        appointment.save()

        Notification.send(
            recipient=appointment.patient,
            title='Appointment Completed',
            message=f'Your appointment on {appointment.appointment_date} has been marked as completed. You can now leave a review.',
            notification_type='appointment_completed',
        )

        messages.success(request, 'Appointment marked as completed.')
        return redirect('appointments:my_appointments')

    return render(request, 'appointments/complete.html', {'appointment': appointment})
