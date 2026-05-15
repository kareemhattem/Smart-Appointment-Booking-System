from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from accounts.models import User
from appointments.models import Appointment
from providers.models import Category, ProviderProfile
from notifications.models import Notification
from reviews.models import Review


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    categories = Category.objects.annotate(provider_count=Count('providers')).order_by('-provider_count')[:6]
    total_providers = User.objects.filter(role='provider').count()
    total_appointments = Appointment.objects.filter(status='completed').count()
    total_users = User.objects.filter(role='user').count()

    featured_providers = []
    for p in User.objects.filter(role='provider')[:6]:
        try:
            profile = p.provider_profile
            avg = p.received_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            featured_providers.append({'user': p, 'profile': profile, 'avg_rating': round(avg, 1)})
        except ProviderProfile.DoesNotExist:
            pass

    return render(request, 'dashboard/landing.html', {
        'categories': categories,
        'total_providers': total_providers,
        'total_appointments': total_appointments,
        'total_users': total_users,
        'featured_providers': featured_providers,
    })


@login_required
def home(request):
    user = request.user
    if user.is_admin():
        return admin_dashboard(request)
    elif user.is_provider():
        return provider_dashboard(request)
    else:
        return user_dashboard(request)


@login_required
def user_dashboard(request):
    user = request.user
    today = timezone.now().date()

    upcoming = Appointment.objects.filter(
        patient=user,
        appointment_date__gte=today,
        status__in=['pending', 'confirmed'],
    ).select_related('provider')[:5]

    recent = Appointment.objects.filter(patient=user).select_related('provider')[:5]
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False)[:5]

    stats = {
        'total': Appointment.objects.filter(patient=user).count(),
        'upcoming': Appointment.objects.filter(patient=user, appointment_date__gte=today, status__in=['pending', 'confirmed']).count(),
        'completed': Appointment.objects.filter(patient=user, status='completed').count(),
        'cancelled': Appointment.objects.filter(patient=user, status='cancelled').count(),
    }

    return render(request, 'dashboard/user_dashboard.html', {
        'upcoming': upcoming,
        'recent': recent,
        'unread_notifications': unread_notifications,
        'stats': stats,
    })


@login_required
def provider_dashboard(request):
    user = request.user
    today = timezone.now().date()

    upcoming = Appointment.objects.filter(
        provider=user,
        appointment_date__gte=today,
        status__in=['pending', 'confirmed'],
    ).select_related('patient').order_by('appointment_date', 'start_time')[:10]

    pending = Appointment.objects.filter(provider=user, status='pending').select_related('patient')
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False)[:5]

    stats = {
        'total': Appointment.objects.filter(provider=user).count(),
        'pending': Appointment.objects.filter(provider=user, status='pending').count(),
        'confirmed': Appointment.objects.filter(provider=user, status='confirmed').count(),
        'completed': Appointment.objects.filter(provider=user, status='completed').count(),
        'avg_rating': user.received_reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
        'total_reviews': user.received_reviews.count(),
    }
    stats['avg_rating'] = round(stats['avg_rating'], 1)

    return render(request, 'dashboard/provider_dashboard.html', {
        'upcoming': upcoming,
        'pending': pending,
        'unread_notifications': unread_notifications,
        'stats': stats,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    stats = {
        'total_users': User.objects.filter(role='user').count(),
        'total_providers': User.objects.filter(role='provider').count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'completed_appointments': Appointment.objects.filter(status='completed').count(),
        'total_reviews': Review.objects.count(),
        'total_categories': Category.objects.count(),
    }

    recent_appointments = Appointment.objects.select_related('patient', 'provider').order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:5]

    return render(request, 'dashboard/admin_dashboard.html', {
        'stats': stats,
        'recent_appointments': recent_appointments,
        'recent_users': recent_users,
    })


@login_required
def admin_users(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    role_filter = request.GET.get('role', '')
    search = request.GET.get('search', '')

    users = User.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search))

    return render(request, 'dashboard/admin_users.html', {
        'users': users,
        'role_filter': role_filter,
        'search': search,
    })


@login_required
def admin_toggle_user(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('dashboard:admin_users')

    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('dashboard:admin_users')


@login_required
def admin_appointments(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.select_related('patient', 'provider').order_by('-created_at')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    return render(request, 'dashboard/admin_appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
    })
