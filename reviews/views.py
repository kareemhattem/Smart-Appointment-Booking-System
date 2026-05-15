from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from appointments.models import Appointment
from notifications.models import Notification


@login_required
def leave_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, patient=request.user, status='completed')

    if hasattr(appointment, 'review'):
        messages.info(request, 'You have already reviewed this appointment.')
        return redirect('appointments:my_appointments')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.reviewer = request.user
            review.provider = appointment.provider
            review.save()

            Notification.send(
                recipient=appointment.provider,
                title='New Review Received',
                message=f'{request.user.get_full_name() or request.user.username} left you a {review.rating}-star review.',
                notification_type='new_review',
            )

            messages.success(request, 'Review submitted. Thank you!')
            return redirect('appointments:my_appointments')
    else:
        form = ReviewForm()

    return render(request, 'reviews/leave_review.html', {'form': form, 'appointment': appointment})


@login_required
def provider_reviews(request, provider_id):
    from accounts.models import User
    from django.db.models import Avg
    provider = get_object_or_404(User, pk=provider_id, role='provider')
    reviews = Review.objects.filter(provider=provider).select_related('reviewer')
    avg = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    return render(request, 'reviews/provider_reviews.html', {
        'provider': provider,
        'reviews': reviews,
        'avg_rating': round(avg, 1),
    })
